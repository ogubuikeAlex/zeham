# nansen/enricher.py
#
# The "NansenEnricher" component the ADR names in its architecture (System
# Overview) but never provided code for. It owns the enrichment side-effect that
# the ADR had inlined in EventListener._enrich:
#   - dedupes addresses,
#   - serves repeat addresses from a TTL cache (review fix: "Nansen caching"),
#   - calls the Nansen client only for cache misses,
#   - writes nansen_labels + status back via the repository,
#   - sets DONE when at least one address resolved, else UNAVAILABLE (NFR-06: the
#     event is never dropped because Nansen failed).
import logging
import time

from constants import NansenStatus
from metrics import metrics
from .client import NansenClient

logger = logging.getLogger(__name__)


class NansenEnricher:
    def __init__(self, client: NansenClient, repo, cache_ttl_seconds: int = 300):
        self.client = client
        self.repo = repo
        self.ttl = cache_ttl_seconds
        self._cache: dict[str, tuple[float, dict]] = {}  # address -> (expiry_monotonic, payload)

    def _cache_get(self, address: str):
        hit = self._cache.get(address)
        if hit and hit[0] > time.monotonic():
            return hit[1]
        if hit:
            del self._cache[address]
        return None

    def _cache_put(self, address: str, payload: dict):
        self._cache[address] = (time.monotonic() + self.ttl, payload)

    async def enrich(self, event_id: str, addresses: list[str]) -> None:
        addresses = [a for a in dict.fromkeys(a for a in addresses if a)]  # dedupe, drop None
        if not addresses:
            await self.repo.update_nansen(event_id, {}, NansenStatus.DONE.value)
            metrics.incr('enrich_done')
            return

        labels: dict = {}
        to_fetch: list[str] = []
        for addr in addresses:
            cached = self._cache_get(addr)
            if cached is not None:
                labels[addr] = cached
            else:
                to_fetch.append(addr)

        try:
            if to_fetch:
                fetched = await self.client.get_labels(to_fetch)
                for addr, payload in fetched.items():
                    labels[addr] = payload
                    if isinstance(payload, dict) and 'error' not in payload:
                        self._cache_put(addr, payload)

            any_ok = any(isinstance(v, dict) and 'error' not in v for v in labels.values())
            status = NansenStatus.DONE if any_ok else NansenStatus.UNAVAILABLE
            await self.repo.update_nansen(event_id, labels, status.value)
            metrics.incr('enrich_done' if any_ok else 'enrich_unavailable')
        except Exception as e:
            # NFR-06: never drop the event because of a third-party API failure.
            logger.warning('enrichment failed', extra={'event_id': event_id, 'error': str(e)})
            await self.repo.update_nansen(event_id, None, NansenStatus.UNAVAILABLE.value)
            metrics.incr('enrich_unavailable')
