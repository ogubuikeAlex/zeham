from collections import defaultdict
from typing import Optional

from constants import Severity, AnomalyType
from .base import BaseRule, RuleAlert, labels_of

WHALE_EVENT_COUNT_THRESHOLD = 5
SMART_MONEY_LABELS = ['smart money', 'whale', 'fund', 'vc', 'institution']
SUSPICIOUS_LABELS = ['mixer', 'tornado', 'unknown', 'new wallet']


class WhaleMoveRule(BaseRule):
    name = 'WhaleMoveRule'
    anomaly_type = AnomalyType.WHALE.value

    def evaluate(self, events: list[dict]) -> Optional[RuleAlert]:
        wallet_events: dict[str, list[dict]] = defaultdict(list)
        for e in events:
            if e.get('from_address'):
                wallet_events[e['from_address']].append(e)
            if e.get('to_address'):
                wallet_events[e['to_address']].append(e)

        for wallet, evts in wallet_events.items():
            if len(evts) < WHALE_EVENT_COUNT_THRESHOLD:
                continue

            label_str = str(labels_of(evts[0])).lower()
            is_smart_money = any(l in label_str for l in SMART_MONEY_LABELS)
            is_suspicious = any(l in label_str for l in SUSPICIOUS_LABELS)

            if is_suspicious:
                severity = Severity.HIGH.value
                reason = (
                    f'Whale activity from a suspicious wallet ({wallet[:16]}...): '
                    f'{len(evts)} events in 60s. Nansen label suggests mixer or new wallet. '
                    'High probability of post-exploit fund movement.'
                )
            elif is_smart_money:
                severity = Severity.MEDIUM.value
                reason = (
                    f'Smart money whale move from {wallet[:16]}...: '
                    f'{len(evts)} events in 60s. Possible market-moving position change.'
                )
            else:
                severity = Severity.LOW.value
                reason = (
                    f'High-frequency wallet activity: {wallet[:16]}... '
                    f'triggered {len(evts)} events in 60s.'
                )

            return RuleAlert(
                rule_name=self.name,
                severity=severity,
                anomaly_type=self.anomaly_type,
                reason=reason,
                confidence=0.75,
                event_ids=[e['id'] for e in evts if e.get('id')],
            )
        return None
