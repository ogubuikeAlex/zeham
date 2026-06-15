import asyncio
import contextlib
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from logging_config import configure_logging
from db.database import init_db, engine
from db.repository import EventRepository
from nansen.client import NansenClient
from nansen.enricher import NansenEnricher
from listener.event_listener import EventListener
from agent.engine import DetectionEngine
from broadcaster.broadcaster import AlertBroadcaster
from scheduler import build_scheduler
from api.watch import router as watch_router
from api.health import router as health_router
from api.subscriptions import router as subscriptions_router
from api.alerts import router as alerts_router
from api.contracts import router as contracts_router
from api.heatmap import router as heatmap_router
from api.agent import router as agent_router
from ws.connection_manager import manager

configure_logging(settings.log_level, settings.log_json)
logger = logging.getLogger(__name__)


async def _start_telegram_commands():
    if not (settings.telegram_commands_enabled and settings.telegram_bot_token):
        logger.info('telegram command bot disabled (no token / disabled)')
        return None
    try:
        from broadcaster.telegram_commands import build_telegram_app
        app = build_telegram_app()
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        logger.info('telegram command bot started (long polling)')
        return app
    except Exception:
        logger.exception('telegram command bot failed to start; continuing without it')
        return None


async def _stop_telegram_commands(app) -> None:
    if app is None:
        return
    with contextlib.suppress(Exception):
        if app.updater and app.updater.running:
            await app.updater.stop()
        await app.stop()
        await app.shutdown()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    repo = EventRepository()
    nansen = NansenClient()
    enricher = NansenEnricher(nansen, repo, settings.nansen_cache_ttl_seconds)
    listener = EventListener(repo, enricher)
    await listener.load_watched_contracts()

    engine = DetectionEngine()

    broadcaster = AlertBroadcaster()
    scheduled_broadcaster = broadcaster if broadcaster.has_channel else None
    if scheduled_broadcaster is None:
        logger.warning('broadcaster idle: no Telegram or Discord channel configured')

    scheduler = build_scheduler(repo, enricher, engine, scheduled_broadcaster)
    scheduler.start()

    telegram_app = await _start_telegram_commands()

    app.state.listener = listener
    app.state.engine = engine
    app.state.broadcaster = broadcaster
    app.state.scheduler = scheduler
    app.state.telegram_app = telegram_app
    listener_task = asyncio.create_task(listener.start())
    logger.info('startup complete', extra={'network': settings.mantle_network.value})

    try:
        yield
    finally:
        logger.info('shutting down')
        await listener.stop()
        scheduler.shutdown(wait=False)
        await _stop_telegram_commands(telegram_app)
        listener_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await listener_task
        dispose = getattr(engine, 'dispose', None)
        if callable(dispose):
            with contextlib.suppress(Exception):
                await dispose()


app = FastAPI(title='Zeham Listener (ADR-001)', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(watch_router)
app.include_router(health_router)
app.include_router(subscriptions_router)
app.include_router(alerts_router)
app.include_router(contracts_router)
app.include_router(heatmap_router)
app.include_router(agent_router)


@app.websocket('/ws/alerts')
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)
