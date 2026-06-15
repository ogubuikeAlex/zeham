import logging

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from config import settings
from db.database import AsyncSessionLocal
from db.models import Alert, DetectionLog

logger = logging.getLogger(__name__)

router = APIRouter()

_AGENT_NAME = 'Zeham Mantis Agent'
_AGENT_VERSION = '0.1.0'
_AGENT_DESCRIPTION = 'On-chain AI security monitor logging anomaly decisions through ERC-8004.'


@router.get('/agent/log')
async def get_agent_log(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(DetectionLog).order_by(DetectionLog.logged_at.desc()).limit(limit).offset(offset)
        )
        rows = result.scalars().all()
    return [
        {
            'id': str(r.id),
            'contract_address': r.contract_address,
            'prompt': (r.prompt or '')[:500] if r.prompt else None,
            'raw_response': r.raw_response,
            'event_ids': r.event_ids,
            'logged_at': r.logged_at.isoformat() if r.logged_at else None,
            'on_chain_tx': None,
        }
        for r in rows
    ]


def _agent_wallet() -> str:
    """Derive the agent's public address from the configured private key (best effort)."""
    if not settings.agent_private_key:
        return ''
    try:
        from eth_account import Account
        return Account.from_key(settings.agent_private_key).address
    except Exception:
        logger.warning('could not derive agent wallet from private key')
        return ''


@router.get('/agent/identity')
async def get_agent_identity():
    async with AsyncSessionLocal() as session:
        total_decisions = await session.scalar(
            select(func.count()).select_from(Alert).where(Alert.on_chain_tx.isnot(None))
        )
    return {
        'name': _AGENT_NAME,
        'version': _AGENT_VERSION,
        'description': _AGENT_DESCRIPTION,
        'agent_wallet': _agent_wallet(),
        'contract_address': settings.erc8004_contract_address or '',
        'deployed_at': '',
        'total_decisions': total_decisions or 0,
    }
