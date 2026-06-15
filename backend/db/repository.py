import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, or_

from sqlalchemy.exc import IntegrityError

from constants import NansenStatus
from .database import AsyncSessionLocal
from .models import Event, WatchedContract, DeadLetter

logger = logging.getLogger(__name__)


def _to_jsonable(value):
    """Recursively coerce web3 types (HexBytes, bytes, AttributeDict) to JSON-safe."""
    if isinstance(value, (bytes, bytearray)):
        return '0x' + value.hex()
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return value.hex() if hasattr(value, 'hex') else str(value)
    except Exception:
        return str(value)


def _normalize_address(value):
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        value = value.hex()
    value = str(value)
    if value[:2] in ('0x', '0X'):
        value = value[2:]
    value = value[-40:]
    return '0x' + value.lower() if value else None


def _normalize_hash(value):
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        value = value.hex()
    value = str(value)
    return value if value.startswith('0x') else '0x' + value


def _to_datetime(ts):
    if isinstance(ts, datetime):
        return ts
    return datetime.fromtimestamp(int(ts), tz=timezone.utc)


class EventRepository:
    async def get_active_contract_addresses(self) -> list[str]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(WatchedContract.address).where(WatchedContract.active.is_(True))
            )
            return [row[0] for row in result.all()]

    async def add_watched_contract(self, address: str, label: str | None = None):
        address = _normalize_address(address)
        async with AsyncSessionLocal() as session:
            existing = await session.execute(
                select(WatchedContract).where(WatchedContract.address == address)
            )
            row = existing.scalar_one_or_none()
            if row:
                row.active = True
                if label:
                    row.label = label
            else:
                session.add(WatchedContract(address=address, label=label, active=True))
            await session.commit()
            logger.info('watched contract upserted', extra={'address': address})

    async def insert_event(self, data: dict) -> str:
        event = Event(
            tx_hash=_normalize_hash(data.get('tx_hash')),
            block_number=int(data['block_number']),
            block_timestamp=_to_datetime(data['block_timestamp']),
            contract_address=_normalize_address(data.get('contract_address')),
            event_type=data['event_type'],
            from_address=_normalize_address(data.get('from_address')),
            to_address=_normalize_address(data.get('to_address')),
            raw_data=_to_jsonable(data.get('raw_data')),
            log_index=int(data['log_index']),
            nansen_status=str(data.get('nansen_status', NansenStatus.PENDING.value)),
        )
        async with AsyncSessionLocal() as session:
            session.add(event)
            try:
                await session.commit()
                return event.id
            except IntegrityError:
                await session.rollback()
                existing = await session.execute(
                    select(Event.id).where(
                        Event.tx_hash == event.tx_hash,
                        Event.log_index == event.log_index,
                    )
                )
                row = existing.first()
                logger.info(
                    'duplicate event ignored',
                    extra={'tx_hash': event.tx_hash, 'log_index': event.log_index},
                )
                return row[0] if row else None

    async def update_nansen(self, event_id: str, labels: dict | None, status: str):
        async with AsyncSessionLocal() as session:
            event = await session.get(Event, event_id)
            if event is None:
                logger.warning('update_nansen: event not found', extra={'event_id': event_id})
                return
            event.nansen_labels = _to_jsonable(labels) if labels is not None else None
            event.nansen_status = str(status)
            await session.commit()

    async def get_unenriched_events(self, limit: int = 50) -> list[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Event.id, Event.from_address, Event.to_address)
                .where(
                    or_(
                        Event.nansen_status == NansenStatus.PENDING.value,
                        Event.nansen_status == NansenStatus.UNAVAILABLE.value,
                    )
                )
                .order_by(Event.created_at.asc())
                .limit(limit)
            )
            return [
                {'id': r[0], 'from_address': r[1], 'to_address': r[2]}
                for r in result.all()
            ]

    async def get_max_block(self) -> int | None:
        """Highest block ever stored — the reconnect/cold-start backfill cursor."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(func.max(Event.block_number)))
            return result.scalar_one_or_none()

    async def record_dead_letter(self, tx_hash, log_index, error: str, payload: dict | None):
        async with AsyncSessionLocal() as session:
            session.add(DeadLetter(
                tx_hash=_normalize_hash(tx_hash),
                log_index=int(log_index) if log_index is not None else None,
                error=error[:2000] if error else None,
                payload=_to_jsonable(payload),
            ))
            await session.commit()
            logger.error(
                'event sent to dead-letter',
                extra={'tx_hash': str(tx_hash), 'log_index': log_index, 'error': error},
            )
