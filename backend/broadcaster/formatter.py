import html
from datetime import datetime

from config import settings

SEVERITY_EMOJI = {
    "CRITICAL": "🚨",
    "HIGH":     "🔴",
    "MEDIUM":   "🟡",
    "LOW":      "⚪",
}

SEVERITY_COLOURS = {
    "CRITICAL": 0xFF0000,   
    "HIGH":     0xFF6B00,   
    "MEDIUM":   0xFFCC00,   
    "LOW":      0x888888,   
}

ANOMALY_LABELS = {
    "flash_loan":         "Flash Loan Attack",
    "rug_pull":           "Rug Pull / Liquidity Drain",
    "whale":              "Whale Move",
    "wash_trade":         "Wash Trading",
    "exploit":            "Contract Exploit",
    "suspicious_pattern": "Suspicious Pattern",
    "none":               "Clean Scan",
}


def _explorer_base() -> str:
    return settings.mantle_explorer_base.rstrip("/")


def _confidence_pct(alert: dict) -> str:
    return f"{int((alert.get('confidence') or 0) * 100)}%"


def _source_label(alert: dict, *, short: bool = False) -> str:
    if alert.get("source") == "AI":
        return "🤖 AI" if short else "🤖 AI Detection"
    return "📏 Rule" if short else "📏 Rule Engine"


def format_alert_telegram(alert: dict) -> str:
    """Format an alert into a Telegram HTML message (NFR-07: mobile-readable)."""
    base          = _explorer_base()
    emoji         = SEVERITY_EMOJI.get(alert["severity"], "⚪")
    anomaly_label = html.escape(ANOMALY_LABELS.get(alert["anomaly_type"], alert["anomaly_type"]))
    contract      = alert["contract_address"]
    contract_short = f"{contract[:8]}...{contract[-6:]}" if len(contract) > 14 else contract
    contract_link = f"{base}/address/{contract}"
    reason        = html.escape(alert["reason"][:200])

    message = (
        f"{emoji} <b>MantisSIEM Alert — {alert['severity']}</b>\n\n"
        f"<b>Type:</b> {anomaly_label}\n"
        f"<b>Contract:</b> <a href='{contract_link}'><code>{contract_short}</code></a>\n"
        f"<b>Reason:</b> {reason}\n"
        f"<b>Confidence:</b> {_confidence_pct(alert)}\n"
        f"<b>Source:</b> {_source_label(alert)}"
    )

    if alert.get("recommended_action"):
        message += f"\n<b>Action:</b> {html.escape(alert['recommended_action'][:120])}"

    if alert.get("on_chain_tx"):
        message += (
            f"\n🔗 <a href=\"{base}/tx/{alert['on_chain_tx']}\">"
            f"View decision on Mantle Explorer</a>"
        )
    return message


def format_alert_discord(alert: dict) -> dict:
    """Format an alert into a Discord embed payload (FR-06)."""
    base          = _explorer_base()
    emoji         = SEVERITY_EMOJI.get(alert["severity"], "⚪")
    anomaly_label = ANOMALY_LABELS.get(alert["anomaly_type"], alert["anomaly_type"])
    contract      = alert["contract_address"]

    fields = [
        {"name": "Anomaly Type",     "value": anomaly_label,                        "inline": True},
        {"name": "Severity",         "value": f"{emoji} {alert['severity']}",       "inline": True},
        {"name": "Confidence",       "value": _confidence_pct(alert),               "inline": True},
        {"name": "Contract",         "value": f"[`{contract[:20]}...`]({base}/address/{contract})", "inline": False},
        {"name": "Reason",           "value": alert["reason"][:200],                "inline": False},
        {"name": "Detection Source", "value": _source_label(alert, short=True),     "inline": True},
    ]

    if alert.get("recommended_action"):
        fields.append({"name": "Recommended Action", "value": alert["recommended_action"][:120], "inline": False})

    if alert.get("on_chain_tx"):
        fields.append({
            "name":   "On-Chain Record",
            "value":  f"[View decision on Mantle Explorer]({base}/tx/{alert['on_chain_tx']})",
            "inline": False,
        })

    fired_at = alert.get("fired_at")
    if isinstance(fired_at, datetime):
        timestamp = fired_at.isoformat()
    elif isinstance(fired_at, str) and fired_at:
        timestamp = fired_at
    else:
        timestamp = None

    return {
        "embeds": [{
            "title":       f"{emoji} MantisSIEM Security Alert",
            "description": f"**{alert['severity']} severity anomaly detected on Mantle Network**",
            "color":       SEVERITY_COLOURS.get(alert["severity"], 0x888888),
            "fields":      fields,
            "footer":      {"text": f"MantisSIEM v1.0.0 · Mantle Network · Alert ID: {str(alert['id'])[:8]}"},
            "timestamp":   timestamp,
        }]
    }
