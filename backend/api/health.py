import logging

from fastapi import APIRouter, Request
from sqlalchemy import text

from db.database import AsyncSessionLocal
from metrics import metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/health')
async def health(request: Request):
    db_ok = False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text('SELECT 1'))
        db_ok = True
    except Exception as e:
        logger.warning('health DB probe failed', extra={'error': str(e)})

    listener = getattr(request.app.state, 'listener', None)
    listener_active = bool(listener and listener.is_healthy())
    watching = len(listener.watched_addresses) if listener else 0

    status = 'ok' if (db_ok and listener_active) else 'degraded'
    return {
        'status': status,
        'db': 'ok' if db_ok else 'unreachable',
        'listener_active': listener_active,
        'watching': watching,
    }


@router.get('/stats')
async def stats():
    return metrics.snapshot()
