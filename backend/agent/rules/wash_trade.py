from typing import Optional

from constants import Severity, AnomalyType
from constants import EventType
from .base import BaseRule, RuleAlert

WASH_TRADE_REPEAT_THRESHOLD = 3  


class WashTradeRule(BaseRule):
    name = 'WashTradeRule'
    anomaly_type = AnomalyType.WASH_TRADE.value

    def evaluate(self, events: list[dict]) -> Optional[RuleAlert]:
        swaps = [e for e in events if e.get('event_type') == EventType.SWAP.value]
        if len(swaps) < WASH_TRADE_REPEAT_THRESHOLD:
            return None

        senders = {e['from_address'] for e in swaps if e.get('from_address')}
        receivers = {e['to_address'] for e in swaps if e.get('to_address')}
        overlap = senders & receivers
        if not overlap:
            return None

        for wallet in overlap:
            as_sender = [e for e in swaps if e.get('from_address') == wallet]
            as_receiver = [e for e in swaps if e.get('to_address') == wallet]
            if len(as_sender) >= 2 and len(as_receiver) >= 2:
                # de-dupe while preserving order
                ids = list(dict.fromkeys(
                    e['id'] for e in (as_sender + as_receiver) if e.get('id')))
                return RuleAlert(
                    rule_name=self.name,
                    severity=Severity.MEDIUM.value,
                    anomaly_type=self.anomaly_type,
                    reason=(
                        f'Wash trading pattern: wallet {wallet[:16]}... appears as both sender '
                        f'({len(as_sender)}x) and receiver ({len(as_receiver)}x) in swap events '
                        'within a single 60-second window on the same contract. '
                        'Volume inflation likely.'
                    ),
                    confidence=0.78,
                    event_ids=ids,
                )
        return None
