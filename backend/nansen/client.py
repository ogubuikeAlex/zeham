# nansen/client.py
# Nansen API HTTP client (httpx async). Source of truth: ADR-001
# "nansen/client.py — Nansen API Client".
#
# Fixes vs the ADR snippet:
#   - Handles HTTP 429 by honoring Retry-After with a bounded number of retries
#     (review fix: "Nansen rate-limiting").
#   - Reuses a single AsyncClient across the call instead of per-address churn.
import asyncio
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3


class NansenClient:
    def __init__(self):
        self.base_url = settings.nansen_base_url
        self.headers = {'x-api-key': settings.nansen_api_key}

    async def _get_one(self, client: httpx.AsyncClient, address: str) -> dict:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.get(f'{self.base_url}/labels', params={'address': address})
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get('Retry-After', 2 ** attempt))
                    logger.warning('nansen rate-limited',
                                   extra={'address': address, 'retry_after_s': retry_after,
                                          'attempt': attempt})
                    await asyncio.sleep(min(retry_after, 30.0))
                    continue
                resp.raise_for_status()
                data = resp.json()
                logger.info('nansen label fetched', extra={'address': address})
                return data
            except httpx.HTTPStatusError as e:
                logger.warning('nansen http error', extra={'address': address,
                                                           'status': e.response.status_code})
                return {'error': f'http_{e.response.status_code}'}
            except Exception as e:
                logger.warning('nansen request failed',
                               extra={'address': address, 'error': str(e), 'attempt': attempt})
                if attempt == _MAX_RETRIES:
                    return {'error': str(e)}
                await asyncio.sleep(2 ** attempt)
        return {'error': 'rate_limited'}

    async def get_labels(self, addresses: list[str]) -> dict:
        if not addresses:
            return {}
        async with httpx.AsyncClient(headers=self.headers, timeout=8.0) as client:
            results = {}
            for address in addresses:
                results[address] = await self._get_one(client, address)
            return results
