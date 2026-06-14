from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from config import settings
from db.database import AsyncSessionLocal
from db.models import Alert


class Deduplicator:
    def __init__(self, window_minutes: int | None = None):
        self.window_minutes = window_minutes or settings.dedup_window_minutes

    async def is_duplicate(self, alert: dict) -> bool:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.window_minutes)
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Alert.id).where(
                    Alert.contract_address == alert["contract_address"],
                    Alert.anomaly_type == alert["anomaly_type"],
                    Alert.notified.is_(True),
                    Alert.notified_at >= cutoff,
                    Alert.id != alert["id"],
                ).limit(1)
            )
            return result.scalar_one_or_none() is not None
