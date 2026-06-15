import asyncio
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Tracks connected dashboard clients and fans alert rows out to all of them.

    A single module-level `manager` instance is shared by the /ws/alerts endpoint
    (which registers connections) and AlertWriter (which broadcasts on every write).
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info('ws client connected', extra={'clients': len(self.active_connections)})

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info('ws client disconnected', extra={'clients': len(self.active_connections)})

    async def broadcast(self, data: dict) -> None:
        """Send a JSON payload to every connected client; drop any that fail."""
        payload = json.dumps(data, default=str)
        async with self._lock:
            targets = list(self.active_connections)
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self.active_connections:
                        self.active_connections.remove(ws)


manager = ConnectionManager()
