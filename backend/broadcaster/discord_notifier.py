import logging

import httpx

from config import settings
from broadcaster.formatter import format_alert_discord

logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self):
        self.webhook_url = settings.discord_webhook_url
        self.enabled = bool(self.webhook_url)
        if not self.enabled:
            logger.warning(
                "Discord notifier disabled (DISCORD_WEBHOOK_URL not set)")

    async def send_alert(self, alert: dict) -> bool:
        """Send a single CRITICAL/HIGH alert as a Discord embed. True on success."""
        if not self.enabled:
            return False
        try:
            payload = format_alert_discord(alert)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
            logger.info(
                f"Discord alert sent: {alert['id']} [{alert['severity']}]")
            return True
        except Exception as e:
            logger.error(f"Discord send failed for alert {alert['id']}: {e}")
            return False

    async def send_digest(self, alerts: list[dict]) -> bool:
        """Send a batched digest of MEDIUM/LOW alerts as a single embed."""
        if not self.enabled or not alerts:
            return True if not alerts else False
        try:
            lines = "\n".join([
                f"• **{a['severity']}** · {a['anomaly_type'].replace('_', ' ').title()} · "
                f"`{a['contract_address'][:16]}...`"
                for a in alerts
            ])
            payload = {
                "embeds": [{
                    "title":       f"📋 Zeham Digest — {len(alerts)} Alerts",
                    "description": lines[:2000],
                    "color":       0xFFCC00,
                    "footer":      {"text": "Zeham v1.0.0 · Mantle Network"},
                }]
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
            logger.info(f"Discord digest sent: {len(alerts)} alerts")
            return True
        except Exception as e:
            logger.error(f"Discord digest failed: {e}")
            return False
