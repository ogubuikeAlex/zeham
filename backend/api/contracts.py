from fastapi import APIRouter
from sqlalchemy import func, select

from db.database import AsyncSessionLocal
from db.models import Event, WatchedContract

router = APIRouter()


@router.get('/contracts')
async def get_contracts():
    """Watched contracts plus a COUNT of stored events for each address."""
    async with AsyncSessionLocal() as session:
        # event counts grouped by address, joined back onto the watched list
        counts = dict(
            (await session.execute(
                select(Event.contract_address, func.count())
                .group_by(Event.contract_address)
            )).all()
        )
        result = await session.execute(
            select(WatchedContract).order_by(WatchedContract.added_at.desc())
        )
        contracts = result.scalars().all()

    return [
        {
            'id': str(c.id),
            'address': c.address,
            'label': c.label,
            'active': c.active,
            'added_at': c.added_at.isoformat() if c.added_at else None,
            'event_count': counts.get(c.address, 0),
        }
        for c in contracts
    ]
