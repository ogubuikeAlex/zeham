# nansen/models.py
#
# NOTE: This file has NO source code in ADR-001, and the file does NOT specify the
# concrete shape of the Nansen `/labels` response. The folder structure lists it as
# "Pydantic models for Nansen API response". FR-04 names the labels Zeham cares
# about: 'Smart Money', 'Known Exploiter', 'Whale', 'CEX Deposit'.
#
# Because the exact JSON schema is UNSPECIFIED in the ADR (a real value that is
# MISSING), these models are intentionally permissive: they validate the address
# and accept the raw label payload as-is (model_config extra='allow'), so no real
# response is rejected. Tighten the fields once the Nansen response schema is known.
from pydantic import BaseModel, ConfigDict


class NansenLabel(BaseModel):
    """One address's enrichment result. Passthrough until the schema is pinned."""
    model_config = ConfigDict(extra='allow')

    address: str | None = None
    labels: list[str] | None = None  # e.g. ['Smart Money', 'Whale'] — per FR-04
    error: str | None = None


class NansenLabelResponse(BaseModel):
    """Maps address -> NansenLabel, mirroring NansenClient.get_labels() output."""
    model_config = ConfigDict(extra='allow')

    results: dict[str, NansenLabel] = {}

    @classmethod
    def from_client(cls, raw: dict) -> 'NansenLabelResponse':
        parsed: dict[str, NansenLabel] = {}
        for address, payload in (raw or {}).items():
            if isinstance(payload, dict):
                parsed[address] = NansenLabel(address=address, **payload)
            else:
                parsed[address] = NansenLabel(address=address)
        return cls(results=parsed)
