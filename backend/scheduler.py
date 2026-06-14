import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings

logger = logging.getLogger(__name__)


def build_scheduler(repo, enricher, engine=None, broadcaster=None) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def reenrich_pending():
        try:
            rows = await repo.get_unenriched_events(limit=settings.enrich_batch_size)
        except Exception as e:
            logger.warning('re-enrich: query failed', extra={'error': str(e)})
            return
        if not rows:
            return
        logger.info('re-enriching events', extra={'count': len(rows)})
        for row in rows:
            await enricher.enrich(row['id'], [row.get('from_address'), row.get('to_address')])

    scheduler.add_job(
        reenrich_pending,
        'interval',
        seconds=settings.enrich_interval_seconds,
        id='reenrich_pending',
        max_instances=1,
        coalesce=True,
    )

    if engine is not None and settings.detection_enabled:
        scheduler.add_job(
            engine.run_cycle,
            'interval',
            seconds=settings.detection_interval_seconds,
            id='detection_cycle',
            max_instances=1,       # NFR-02: no overlapping cycles
            coalesce=True,
            misfire_grace_time=10,
        )
        logger.info('detection cycle scheduled',
                    extra={'interval_s': settings.detection_interval_seconds})

    if broadcaster is not None and settings.broadcaster_enabled:
        scheduler.add_job(
            broadcaster.run_cycle,
            'interval',
            seconds=settings.broadcaster_interval_seconds,
            id='broadcast_cycle',
            max_instances=1,       # NFR-02: no overlapping cycles
            coalesce=True,
            misfire_grace_time=5,
        )
        logger.info('broadcast cycle scheduled',
                    extra={'interval_s': settings.broadcaster_interval_seconds})

    return scheduler
