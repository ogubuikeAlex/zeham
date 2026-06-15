import logging
from datetime import datetime, timezone

from sqlalchemy import select, update

from config import settings
from db.database import AsyncSessionLocal
from db.models import Alert
from broadcaster.telegram_notifier import TelegramNotifier
from broadcaster.discord_notifier import DiscordNotifier
from broadcaster.deduplicator import Deduplicator
from broadcaster.digest import DigestBuffer

logger = logging.getLogger(__name__)


class AlertBroadcaster:
    def __init__(self):
        self.telegram = TelegramNotifier()
        self.discord = DiscordNotifier()
        self.deduplicator = Deduplicator()
        self.digest = DigestBuffer(interval_minutes=settings.digest_interval_minutes)

    @property
    def has_channel(self) -> bool:
        """True if at least one delivery channel is configured."""
        return self.telegram.enabled or self.discord.enabled

    async def run_cycle(self):
        """Called every broadcaster_interval_seconds by APScheduler."""
        try:
            alerts = await self._fetch_unnotified()
            if not alerts:
                if self.digest.should_flush():
                    await self._flush_digest()
                return

            logger.info(f"Broadcaster: processing {len(alerts)} unnotified alerts")
            for alert in alerts:
                await self._route_alert(alert)

            if self.digest.should_flush():
                await self._flush_digest()
        except Exception as e:
            logger.error(f"Broadcaster cycle failed: {e}", exc_info=True)

    async def _fetch_unnotified(self) -> list[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Alert)
                .where(Alert.notified.is_(False))
                .order_by(Alert.fired_at.asc())
                .limit(settings.broadcaster_batch_size)
            )
            rows = result.scalars().all()

        return [
            {
                "id":                 str(r.id),
                "contract_address":   r.contract_address,
                "severity":           r.severity,
                "anomaly_type":       r.anomaly_type,
                "reason":             r.reason,
                "confidence":         r.confidence,
                "source":             r.source,
                "recommended_action": r.recommended_action,
                "on_chain_tx":        r.on_chain_tx,
                "fired_at":           r.fired_at,
            }
            for r in rows
        ]

    async def _route_alert(self, alert: dict):
        severity = alert["severity"]

        if await self.deduplicator.is_duplicate(alert):
            logger.info(f"Duplicate suppressed: {alert['id']} [{severity}]")
            await self._mark_notified(alert["id"])
            return

        if severity in ("CRITICAL", "HIGH"):
            tg_ok = await self.telegram.send_alert(alert)
            dc_ok = await self.discord.send_alert(alert)
            if tg_ok or dc_ok:
                await self._mark_notified(alert["id"])
            else:
                logger.warning(f"Both channels failed for alert {alert['id']}. Will retry.")

        elif severity in ("MEDIUM", "LOW"):
            self.digest.add(alert)
            await self._mark_notified(alert["id"])
            logger.info(f"Alert {alert['id']} [{severity}] buffered for digest")

        else:
            logger.info(f"Alert {alert['id']} severity '{severity}' not broadcast; marking notified")
            await self._mark_notified(alert["id"])

    async def _flush_digest(self):
        items = self.digest.flush()
        if not items:
            return
        logger.info(f"Flushing digest: {len(items)} MEDIUM/LOW alerts")
        await self.telegram.send_digest(items)
        await self.discord.send_digest(items)

    async def _mark_notified(self, alert_id: str):
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Alert)
                .where(Alert.id == alert_id)
                .values(notified=True, notified_at=datetime.now(timezone.utc))
            )
            await session.commit()
