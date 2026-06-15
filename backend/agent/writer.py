import logging

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from constants import AlertSource
from db.database import AsyncSessionLocal
from db.models import Alert, DetectionLog, Event
from ws.connection_manager import manager
from ws.serializers import alert_to_dict
from .chain import ChainLogger

logger = logging.getLogger(__name__)


class AlertWriter:
    def __init__(self, chain: ChainLogger | None = None):
        self.chain = chain or ChainLogger()

    async def _save_alert(self, alert: Alert) -> Alert | None:
        """Insert the alert (idempotent on source_event_ids), then log it on-chain."""
        if alert.source_event_ids:
            alert.source_event_ids = sorted(alert.source_event_ids)
        async with AsyncSessionLocal() as session:
            session.add(alert)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                logger.info('duplicate alert ignored',
                            extra={'source_event_ids': alert.source_event_ids})
                return None
            await session.refresh(alert)

            tx = await self.chain.log_decision(
                alert.anomaly_type, alert.severity, alert.reason,
                contract_target=alert.contract_address, is_anomaly=True,
            )
            if tx:
                alert.on_chain_tx = tx
                await session.commit()
            logger.info('alert written',
                        extra={'alert_id': alert.id, 'severity': alert.severity,
                               'anomaly_type': alert.anomaly_type, 'source': alert.source,
                               'on_chain_tx': alert.on_chain_tx})

        try:
            await manager.broadcast(alert_to_dict(alert))
        except Exception:
            logger.exception('ws broadcast failed', extra={'alert_id': alert.id})
        return alert

    async def write_rule_alert(self, rule_alert, contract: str, events: list[dict]) -> Alert | None:
        return await self._save_alert(Alert(
            contract_address=contract,
            severity=rule_alert.severity,
            anomaly_type=rule_alert.anomaly_type,
            reason=rule_alert.reason,
            confidence=rule_alert.confidence,
            source=AlertSource.RULE.value,
            source_event_ids=rule_alert.event_ids,
        ))

    async def write_ai_alert(self, ai_result: dict, contract: str, events: list[dict],
                             rule_hints: list) -> Alert | None:
        if not ai_result.get('anomaly'):
            logger.info('AI found no anomaly', extra={'contract': contract[:16]})
            return None
        return await self._save_alert(Alert(
            contract_address=contract,
            severity=ai_result['severity'],
            anomaly_type=ai_result['anomaly_type'],
            reason=ai_result['reason'],
            confidence=ai_result.get('confidence', 0.5),
            source=AlertSource.AI.value,
            source_event_ids=[e['id'] for e in events if e.get('id')],
            recommended_action=ai_result.get('recommended_action'),
        ))

    async def mark_processed(self, event_ids: list[str]) -> None:
        if not event_ids:
            return
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(Event).where(Event.id.in_(event_ids)).values(processed=True)
                )
                await session.commit()
        except Exception:
            logger.exception('mark_processed failed', extra={'count': len(event_ids)})

    async def log_detection(self, contract: str, prompt: str, response: str,
                            event_ids: list[str]) -> None:
        try:
            async with AsyncSessionLocal() as session:
                session.add(DetectionLog(
                    contract_address=contract,
                    prompt=(prompt or '')[:4000],
                    raw_response=(response or '')[:2000],
                    event_ids=event_ids,
                ))
                await session.commit()
        except Exception:
            logger.exception('log_detection failed', extra={'contract': contract[:16]})
