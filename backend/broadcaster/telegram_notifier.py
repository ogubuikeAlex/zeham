import html
import logging

from config import settings
from broadcaster.formatter import format_alert_telegram, SEVERITY_EMOJI

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.enabled = bool(self.token and self.chat_id)
        if not self.enabled:
            logger.warning(
                "Telegram notifier disabled (TELEGRAM_BOT_TOKEN/CHAT_ID not set)")

    async def send_alert(self, alert: dict) -> bool:
        """Send a single CRITICAL/HIGH alert immediately. True on success."""
        if not self.enabled:
            return False
        try:
            from telegram import Bot
            from telegram.constants import ParseMode
            message = format_alert_telegram(alert)
            async with Bot(token=self.token) as bot:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            logger.info(
                f"Telegram alert sent: {alert['id']} [{alert['severity']}]")
            return True
        except Exception as e:
            logger.error(f"Telegram send failed for alert {alert['id']}: {e}")
            return False

    async def send_digest(self, alerts: list[dict]) -> bool:
        """Send a batched digest of MEDIUM/LOW alerts."""
        if not alerts:
            return True
        if not self.enabled:
            return False
        try:
            from telegram import Bot
            from telegram.constants import ParseMode
            lines = [f"<b>📋 Zeham Digest — {len(alerts)} alerts</b>\n"]
            for a in alerts:
                emoji = SEVERITY_EMOJI.get(a["severity"], "⚪")
                anomaly = html.escape(
                    a["anomaly_type"].replace("_", " ").title())
                reason = html.escape(a["reason"][:100])
                lines.append(
                    f"{emoji} <b>{a['severity']}</b> · {anomaly}\n"
                    f"   Contract: <code>{a['contract_address'][:20]}...</code>\n"
                    f"   {reason}\n"
                )
            message = "\n".join(lines)
            async with Bot(token=self.token) as bot:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=message[:4096],   # Telegram max message length
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            logger.info(f"Telegram digest sent: {len(alerts)} alerts")
            return True
        except Exception as e:
            logger.error(f"Telegram digest failed: {e}")
            return False
