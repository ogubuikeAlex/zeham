from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RuleAlert:
    rule_name: str
    severity: str           
    anomaly_type: str       
    reason: str             
    confidence: float      
    event_ids: list = field(default_factory=list)


class BaseRule(ABC):
    name: str
    anomaly_type: str

    @abstractmethod
    def evaluate(self, events: list[dict]) -> Optional[RuleAlert]:
        """Return a RuleAlert if an anomaly is detected in this batch, else None."""
        ...


def labels_of(event: dict) -> dict:
    """Safe accessor for an event's Nansen labels."""
    labels = event.get('nansen_labels')
    return labels if isinstance(labels, dict) else {}
