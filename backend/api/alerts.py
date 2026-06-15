from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from db.database import AsyncSessionLocal
from db.models import Alert, WatchedContract
from ws.serializers import alert_to_dict

router = APIRouter()


@router.get('/alerts')
async def get_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    severity: str | None = None,
    type: str | None = None,
):
    query = select(Alert).order_by(Alert.fired_at.desc()).limit(limit).offset(offset)
    if severity and severity.upper() != 'ALL':
        query = query.where(Alert.severity == severity.upper())
    if type:
        query = query.where(Alert.anomaly_type == type.lower())

    async with AsyncSessionLocal() as session:
        result = await session.execute(query)
        rows = result.scalars().all()
    return [alert_to_dict(r) for r in rows]


@router.get('/alerts/stats')
async def get_stats():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    async with AsyncSessionLocal() as session:
        total_today = await session.scalar(
            select(func.count()).select_from(Alert).where(Alert.fired_at >= cutoff)
        )
        critical_today = await session.scalar(
            select(func.count()).select_from(Alert)
            .where(Alert.fired_at >= cutoff, Alert.severity == 'CRITICAL')
        )
        contracts_monitored = await session.scalar(
            select(func.count()).select_from(WatchedContract).where(WatchedContract.active.is_(True))
        )
        on_chain_decisions = await session.scalar(
            select(func.count()).select_from(Alert).where(Alert.on_chain_tx.isnot(None))
        )

    return {
        'total_alerts_today': total_today or 0,
        'critical_today': critical_today or 0,
        'contracts_monitored': contracts_monitored or 0,
        'on_chain_decisions': on_chain_decisions or 0,
    }
