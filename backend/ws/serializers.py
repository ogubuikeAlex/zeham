from db.models import Alert


def alert_to_dict(alert: Alert) -> dict:
    """Serialize an Alert ORM row into the shape the frontend `Alert` type expects."""
    fired_at = alert.fired_at
    return {
        'id': str(alert.id),
        'contract_address': alert.contract_address,
        'severity': alert.severity,
        'anomaly_type': alert.anomaly_type,
        'reason': alert.reason,
        'confidence': alert.confidence,
        'source': alert.source,
        'recommended_action': alert.recommended_action,
        'on_chain_tx': alert.on_chain_tx,
        'fired_at': fired_at.isoformat() if fired_at else None,
    }
