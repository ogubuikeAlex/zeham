import logging
from collections import defaultdict

from sqlalchemy import select

from config import settings
from constants import NansenStatus
from db.database import AsyncSessionLocal
from db.models import Event

logger = logging.getLogger(__name__)


class EventFetcher:
    async def fetch_unprocessed_batches(self) -> list[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Event)
                .where(
                    Event.nansen_status == NansenStatus.DONE.value,
                    Event.processed.is_(False),
                )
                .order_by(Event.block_number.asc())
            )
            events = result.scalars().all()

        if not events:
            return []

        grouped: dict[str, list[dict]] = defaultdict(list)
        for e in events:
            grouped[e.contract_address].append({
                'id': e.id,
                'tx_hash': e.tx_hash,
                'block_number': e.block_number,
                'event_type': e.event_type,
                'from_address': e.from_address,
                'to_address': e.to_address,
                'raw_data': e.raw_data,
                'nansen_labels': e.nansen_labels,
                'nansen_status': e.nansen_status,
            })

        logger.info('fetched unprocessed events',
                    extra={'events': len(events), 'contracts': len(grouped)})
        return [
            {
                'contract_address': addr,
                'events': evts,
                'time_window_seconds': settings.detection_interval_seconds,
            }
            for addr, evts in grouped.items()
        ]
