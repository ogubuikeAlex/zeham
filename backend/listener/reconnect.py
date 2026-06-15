import asyncio
import logging
import functools
import secrets

logger = logging.getLogger(__name__)


def with_reconnect(max_retries=5, base_delay=2.0, max_delay=60.0, on_give_up=None):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_retries:
                try:
                    return await fn(*args, **kwargs)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    attempt += 1
                    backoff = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    jitter = (secrets.randbelow(1000) / 1000.0) * backoff
                    delay = round(jitter, 3)
                    logger.warning(
                        'websocket disconnected; scheduling reconnect',
                        extra={'error': str(e), 'attempt': attempt,
                               'max_retries': max_retries, 'delay_s': delay},
                    )
                    await asyncio.sleep(delay)
            logger.critical('max reconnect retries exceeded; listener stopped',
                            extra={'max_retries': max_retries})
            if on_give_up is not None:
                try:
                    res = on_give_up(*args, **kwargs)
                    if asyncio.iscoroutine(res):
                        await res
                except Exception:
                    logger.exception('on_give_up callback failed')
        return wrapper
    return decorator
