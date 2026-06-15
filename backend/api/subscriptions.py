import re

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import settings
from db.database import AsyncSessionLocal
from db.models import Subscription

router = APIRouter()

_ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


class SubscribeRequest(BaseModel):
    address: str
    telegram_chat_id: str | None = None
    label: str | None = None

    @field_validator("address")
    @classmethod
    def _validate_address(cls, v: str) -> str:
        if not _ADDR_RE.match(v):
            raise ValueError("address must be a 0x-prefixed 40-hex-char EVM address")
        return v.lower()


def _check_auth(x_api_key: str | None, authorization: str | None) -> None:
    expected = settings.watch_api_key
    if not expected:
        return 
    presented = x_api_key
    if not presented and authorization and authorization.lower().startswith("bearer "):
        presented = authorization[7:]
    if presented != expected:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


@router.post("/subscribe")
async def subscribe(
    req: SubscribeRequest,
    request: Request,
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    _check_auth(x_api_key, authorization)

    async with AsyncSessionLocal() as session:
        sub = Subscription(
            contract_address=req.address,
            telegram_chat_id=req.telegram_chat_id,
            label=req.label,
        )
        session.add(sub)
        try:
            await session.commit()
            await session.refresh(sub)
            sub_id = sub.id
        except IntegrityError:
            await session.rollback()
            return {"status": "already_subscribed", "address": req.address}

    try:
        listener = request.app.state.listener
        await listener.add_contract(req.address, req.label or "subscription")
    except Exception:
        pass

    return {"status": "subscribed", "id": sub_id, "address": req.address}


@router.get("/subscriptions")
async def list_subscriptions(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    _check_auth(x_api_key, authorization)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.active.is_(True)).limit(200)
        )
        subs = result.scalars().all()
    return {
        "count": len(subs),
        "subscriptions": [
            {
                "id": s.id,
                "contract_address": s.contract_address,
                "telegram_chat_id": s.telegram_chat_id,
                "label": s.label,
                "added_at": s.added_at.isoformat() if s.added_at else None,
            }
            for s in subs
        ],
    }


@router.delete("/subscribe/{subscription_id}")
async def unsubscribe(
    subscription_id: str,
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    _check_auth(x_api_key, authorization)
    async with AsyncSessionLocal() as session:
        sub = await session.get(Subscription, subscription_id)
        if not sub:
            raise HTTPException(status_code=404, detail="subscription not found")
        sub.active = False
        await session.commit()
    return {"status": "unsubscribed", "id": subscription_id}
