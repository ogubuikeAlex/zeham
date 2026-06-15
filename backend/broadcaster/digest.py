from datetime import datetime, timezone
from typing import Optional

MAX_DIGEST_ITEMS = 50


class DigestBuffer:
    def __init__(self, interval_minutes: int = 10):
        self.interval_minutes = interval_minutes
        self._buffer: list[dict] = []
        self._last_flush: Optional[datetime] = None

    def add(self, alert: dict):
        self._buffer.append(alert)

    def should_flush(self) -> bool:
        if not self._buffer:
            return False
        if self._last_flush is None:
            return True
        elapsed = (datetime.now(timezone.utc) - self._last_flush).total_seconds()
        return elapsed >= self.interval_minutes * 60

    def flush(self) -> list[dict]:
        items = self._buffer[:MAX_DIGEST_ITEMS]
        self._buffer = self._buffer[MAX_DIGEST_ITEMS:]
        self._last_flush = datetime.now(timezone.utc)
        return items
