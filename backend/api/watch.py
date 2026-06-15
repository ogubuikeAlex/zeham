import re

from fastapi import APIRouter, Request, Header, HTTPException
from pydantic import BaseModel, field_validator

from config import settings

router = APIRouter()

_ADDR_RE = re.compile(r'^0x[0-9a-fA-F]{40}$')


class WatchRequest(BaseModel):
    address: str
    label: str | None = None

    @field_validator('address')
    @classmethod
    def _validate_address(cls, v: str) -> str:
        if not _ADDR_RE.match(v):
            raise ValueError('address must be a 0x-prefixed 40-hex-char EVM address')
        return v


def _check_auth(x_api_key: str | None, authorization: str | None) -> None:
    expected = settings.watch_api_key
    if not expected:
        return  # open in dev
    presented = x_api_key
    if not presented and authorization and authorization.lower().startswith('bearer '):
        presented = authorization[7:]
    if presented != expected:
        raise HTTPException(status_code=401, detail='invalid or missing API key')


@router.post('/watch')
async def add_contract(
    req: WatchRequest,
    request: Request,
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    _check_auth(x_api_key, authorization)
    listener = request.app.state.listener
    await listener.add_contract(req.address, req.label)
    return {'status': 'watching', 'address': req.address}
