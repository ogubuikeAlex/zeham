from typing import Optional

from constants import Severity, AnomalyType
from .base import BaseRule, RuleAlert, labels_of

FLASH_LOAN_SIGNATURES = ['flashLoan', 'flashBorrow', 'FlashLoan', 'FLASHLOAN']

MULTI_TYPE_THRESHOLD = 3


class FlashLoanRule(BaseRule):
    name = 'FlashLoanRule'
    anomaly_type = AnomalyType.FLASH_LOAN.value

    def evaluate(self, events: list[dict]) -> Optional[RuleAlert]:
        by_tx: dict[str, list[dict]] = {}
        for e in events:
            by_tx.setdefault(e.get('tx_hash'), []).append(e)

        for tx_hash, tx_events in by_tx.items():
            if not tx_hash:
                continue
            event_types = {e.get('event_type') for e in tx_events}

            # Condition 1: many distinct event types in one tx.
            has_multiple_types = len(event_types) >= MULTI_TYPE_THRESHOLD

            # Condition 2: a flash-loan function signature appears in raw_data.
            has_flash_sig = any(
                any(sig.lower() in str(e.get('raw_data', '')).lower()
                    for sig in FLASH_LOAN_SIGNATURES)
                for e in tx_events
            )

            # Condition 3: Nansen flags the wallet as an exploiter / flashbot.
            nansen = labels_of(tx_events[0])
            is_suspicious_wallet = any(
                'exploiter' in str(v).lower() or 'flashbot' in str(v).lower()
                for v in nansen.values()
            )

            if has_multiple_types and (has_flash_sig or is_suspicious_wallet):
                return RuleAlert(
                    rule_name=self.name,
                    severity=Severity.CRITICAL.value,
                    anomaly_type=self.anomaly_type,
                    reason=(
                        f'Possible flash loan attack in tx {str(tx_hash)[:16]}... '
                        f'Single transaction contains {len(event_types)} distinct event types '
                        f"({', '.join(str(t) for t in event_types)}). "
                        f'Wallet label: {nansen}. '
                        'Pattern matches borrow-manipulate-repay within one block.'
                    ),
                    confidence=0.85 if has_flash_sig else 0.65,
                    event_ids=[e['id'] for e in tx_events if e.get('id')],
                )
        return None
