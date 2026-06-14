import logging
from typing import Optional

from constants import Severity, AnomalyType

logger = logging.getLogger(__name__)

VALID_SEVERITIES = {s.value for s in Severity}
VALID_ANOMALY_TYPES = {a.value for a in AnomalyType}

_REQUIRED_FIELDS = {'anomaly', 'anomaly_type', 'severity', 'confidence', 'reason'}


def parse_ai_response(raw: dict | None) -> Optional[dict]:
    """Return the response dict if it matches the contract, else None."""
    if not isinstance(raw, dict):
        logger.warning('AI response is not a dict')
        return None

    missing = _REQUIRED_FIELDS - raw.keys()
    if missing:
        logger.warning('AI response missing fields', extra={'missing': sorted(missing)})
        return None

    if not isinstance(raw['anomaly'], bool):
        logger.warning('AI anomaly field is not bool')
        return None

    if raw['severity'] not in VALID_SEVERITIES:
        logger.warning('AI returned invalid severity', extra={'severity': raw['severity']})
        return None

    if raw['anomaly_type'] not in VALID_ANOMALY_TYPES:
        logger.warning('AI returned invalid anomaly_type', extra={'anomaly_type': raw['anomaly_type']})
        return None

    if not isinstance(raw.get('confidence'), (int, float)):
        raw['confidence'] = 0.5   # tolerate a missing/odd confidence

    return raw
