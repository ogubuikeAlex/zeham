import threading
import time
from collections import deque


class Metrics:
    def __init__(self, window: int = 1000):
        self._lock = threading.Lock()
        self.events_captured = 0
        self.events_stored = 0
        self.events_dropped = 0         
        self.enrich_done = 0
        self.enrich_unavailable = 0
        self.duplicates_ignored = 0
        # rolling capture->store latencies (seconds) for percentile-ish reporting
        self._latencies: deque[float] = deque(maxlen=window)
        # rolling store timestamps for a 60s throughput estimate
        self._store_times: deque[float] = deque(maxlen=window)

    def incr(self, field: str, n: int = 1) -> None:
        with self._lock:
            setattr(self, field, getattr(self, field) + n)

    def observe_latency(self, seconds: float) -> None:
        with self._lock:
            self._latencies.append(seconds)
            self._store_times.append(time.monotonic())

    def snapshot(self) -> dict:
        with self._lock:
            lat = sorted(self._latencies)
            now = time.monotonic()
            per_min = sum(1 for t in self._store_times if now - t <= 60)

            def pct(p: float) -> float | None:
                if not lat:
                    return None
                idx = min(len(lat) - 1, int(p * len(lat)))
                return round(lat[idx], 4)

            return {
                'events_captured': self.events_captured,
                'events_stored': self.events_stored,
                'events_dropped': self.events_dropped,
                'duplicates_ignored': self.duplicates_ignored,
                'enrich_done': self.enrich_done,
                'enrich_unavailable': self.enrich_unavailable,
                'stored_last_60s': per_min,
                'latency_p50_s': pct(0.50),
                'latency_p95_s': pct(0.95),
                'latency_max_s': round(max(lat), 4) if lat else None,
            }


metrics = Metrics()