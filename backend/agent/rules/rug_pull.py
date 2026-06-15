from typing import Optional

from constants import Severity, AnomalyType
from .base import BaseRule, RuleAlert, labels_of

LIQUIDITY_REMOVAL_EVENTS = ['Burn', 'RemoveLiquidity', 'Withdrawal', 'Transfer']
CONCENTRATION_THRESHOLD = 0.80   
MIN_REMOVAL_EVENTS = 2


class RugPullRule(BaseRule):
    name = 'RugPullRule'
    anomaly_type = AnomalyType.RUG_PULL.value

    def evaluate(self, events: list[dict]) -> Optional[RuleAlert]:
        removal_events = [e for e in events if e.get('event_type') in LIQUIDITY_REMOVAL_EVENTS]
        if not removal_events:
            return None

        from_addresses = [e.get('from_address') for e in removal_events if e.get('from_address')]
        if not from_addresses:
            return None

        most_common = max(set(from_addresses), key=from_addresses.count)
        concentration = from_addresses.count(most_common) / len(from_addresses)

        if concentration >= CONCENTRATION_THRESHOLD and len(removal_events) >= MIN_REMOVAL_EVENTS:
            nansen = labels_of(removal_events[0])
            is_dev_wallet = any(
                'deployer' in str(v).lower() or 'team' in str(v).lower()
                for v in nansen.values()
            )
            severity = Severity.CRITICAL.value if is_dev_wallet else Severity.HIGH.value

            reason = (
                f'Potential rug pull: {len(removal_events)} liquidity removal events in one '
                f'window, {concentration * 100:.0f}% from a single wallet '
                f'({str(most_common)[:16]}...). Nansen label: {nansen}.'
            )
            if is_dev_wallet:
                reason += ' Severity elevated to CRITICAL: wallet is labelled as project deployer/team.'

            return RuleAlert(
                rule_name=self.name,
                severity=severity,
                anomaly_type=self.anomaly_type,
                reason=reason,
                confidence=0.90 if is_dev_wallet else 0.70,
                event_ids=[e['id'] for e in removal_events if e.get('id')],
            )
        return None
