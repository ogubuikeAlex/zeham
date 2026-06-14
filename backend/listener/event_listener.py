import asyncio
import logging
import time
from collections import OrderedDict

from web3 import AsyncWeb3, WebSocketProvider

from config import settings
from constants import NansenStatus
from metrics import metrics
from .decoder import decode_log
from .reconnect import with_reconnect

logger = logging.getLogger(__name__)

_BLOCK_CACHE_MAX = 512


def _mark_stopped(listener, *args, **kwargs):
    """on_give_up callback: keep /health honest when the listener dies."""
    listener._running = False
    listener._connected = False


def _f(log, key, default=None):
    """Field access that works for AttributeDict or plain dict."""
    if hasattr(log, 'get'):
        return log.get(key, default)
    try:
        return log[key]
    except Exception:
        return default


class EventListener:
    def __init__(self, repo, enricher):
        self.repo = repo
        self.enricher = enricher
        self.watched_addresses: list[str] = []
        self._running = False
        self._connected = False
        self._w3 = None
        self._subscription_id = None
        self._last_block: int | None = None
        self._sem = asyncio.Semaphore(settings.max_concurrent_handlers)
        self._block_ts_cache: "OrderedDict[int, int]" = OrderedDict()

    def is_healthy(self) -> bool:
        return self._running and self._connected

    async def load_watched_contracts(self):
        self.watched_addresses = await self.repo.get_active_contract_addresses()
        logger.info('loaded watched contracts', extra={'count': len(self.watched_addresses)})

    async def add_contract(self, address: str, label: str = None):
        await self.repo.add_watched_contract(address, label)
        if address not in self.watched_addresses:
            self.watched_addresses.append(address)
        # FR-08: re-subscribe the live connection so the new contract is watched
        # immediately, without a restart.
        if self._connected and self._w3 is not None:
            await self._subscribe(self._w3)
        logger.info('now watching', extra={'address': address})

    async def stop(self):
        self._running = False
        if self._connected and self._w3 is not None and self._subscription_id is not None:
            try:
                await self._w3.eth.unsubscribe(self._subscription_id)
            except Exception:
                pass

    @with_reconnect(
        max_retries=settings.reconnect_max_retries,
        base_delay=settings.reconnect_base_delay,
        max_delay=settings.reconnect_max_delay,
        on_give_up=_mark_stopped,
    )    
    async def start(self):
        self._running = True
        async with AsyncWeb3(WebSocketProvider(settings.mantle_ws_url)) as w3:
            self._w3 = w3
            self._connected = True
            logger.info('connected to Mantle WebSocket RPC',
                        extra={'network': settings.mantle_network.value})
            await self._backfill(w3)
            await self._subscribe(w3)
            try:
                async for message in w3.socket.process_subscriptions():
                    if not self._running:
                        break
                    raw_log = message.get('result', message) if isinstance(message, dict) else message
                    received_at = time.monotonic()
                    asyncio.create_task(self._handle_event(w3, raw_log, received_at))
            finally:
                self._connected = False
                self._w3 = None

    async def _subscribe(self, w3):
        if self._subscription_id is not None:
            try:
                await w3.eth.unsubscribe(self._subscription_id)
            except Exception:
                pass
            self._subscription_id = None
        if not self.watched_addresses:
            logger.warning('no contracts to watch; idle until /watch is called')
            return
        self._subscription_id = await w3.eth.subscribe('logs', {'address': self.watched_addresses})
        logger.info('subscribed to logs',
                    extra={'subscription': str(self._subscription_id),
                           'count': len(self.watched_addresses)})

    async def _backfill(self, w3):
        """Replay logs missed while disconnected (WS subscriptions do not replay)."""
        if not settings.backfill_on_reconnect or not self.watched_addresses:
            return
        cursor = self._last_block
        if cursor is None:
            cursor = await self.repo.get_max_block()
        if cursor is None:
            return  # cold start, empty DB -> start from "now", nothing to backfill
        try:
            latest = await w3.eth.block_number
        except Exception as e:
            logger.warning('backfill: cannot read latest block', extra={'error': str(e)})
            return
        from_block = int(cursor) + 1
        if from_block > latest:
            return
        logger.info('backfilling missed logs', extra={'from_block': from_block, 'to_block': latest})
        try:
            logs = await w3.eth.get_logs(
                {'fromBlock': from_block, 'toBlock': latest, 'address': self.watched_addresses}
            )
        except Exception as e:
            logger.warning('backfill get_logs failed', extra={'error': str(e)})
            return
        for raw_log in logs:
            # received_at=None -> not counted toward live latency
            asyncio.create_task(self._handle_event(w3, raw_log, None))

    async def _block_ts(self, w3, block_number: int) -> int:
        bn = int(block_number)
        if bn in self._block_ts_cache:
            self._block_ts_cache.move_to_end(bn)
            return self._block_ts_cache[bn]
        block = await w3.eth.get_block(bn)
        ts = block['timestamp']
        self._block_ts_cache[bn] = ts
        if len(self._block_ts_cache) > _BLOCK_CACHE_MAX:
            self._block_ts_cache.popitem(last=False)
        return ts

    async def _handle_event(self, w3, raw_log, received_at):
        async with self._sem:
            try:
                metrics.incr('events_captured')
                block_number = _f(raw_log, 'blockNumber')
                ts = await self._block_ts(w3, block_number)
                decoded = decode_log(raw_log)
                event_id = await self.repo.insert_event({
                    'tx_hash': _f(raw_log, 'transactionHash'),
                    'block_number': block_number,
                    'block_timestamp': ts,
                    'contract_address': _f(raw_log, 'address'),
                    'event_type': decoded['event_type'],
                    'from_address': decoded['from_address'],
                    'to_address': decoded['to_address'],
                    'raw_data': dict(raw_log),
                    'log_index': _f(raw_log, 'logIndex'),
                    'nansen_status': NansenStatus.PENDING.value,
                })
                if event_id is None:
                    metrics.incr('duplicates_ignored')
                    return
                metrics.incr('events_stored')
                if received_at is not None:
                    metrics.observe_latency(time.monotonic() - received_at)
                self._last_block = max(self._last_block or 0, int(block_number))
                logger.info('stored event',
                            extra={'event_id': event_id, 'event_type': decoded['event_type'],
                                   'block_number': int(block_number)})
                asyncio.create_task(self.enricher.enrich(
                    event_id, [decoded['from_address'], decoded['to_address']]))
            except Exception as e:
                metrics.incr('events_dropped')
                logger.exception('error handling event')
                try:
                    await self.repo.record_dead_letter(
                        _f(raw_log, 'transactionHash'), _f(raw_log, 'logIndex'),
                        str(e), dict(raw_log) if hasattr(raw_log, '__iter__') else None)
                except Exception:
                    logger.error('failed to record dead-letter')
