import logging

from constants import Severity
from .fetcher import EventFetcher
from .rules import ALL_RULES
from .ai.elfa_client import ElfaClient
from .ai.altllm_client import AltLLMClient
from .ai.prompt import SYSTEM_PROMPT, build_user_prompt
from .ai.parser import parse_ai_response
from .writer import AlertWriter

logger = logging.getLogger(__name__)


class DetectionEngine:
    def __init__(self):
        self.fetcher = EventFetcher()
        self.rules = ALL_RULES
        self.elfa = ElfaClient()
        self.altllm = AltLLMClient()
        self.writer = AlertWriter()

    async def run_cycle(self) -> None:
        """One detection cycle. Scheduled every detection_interval_seconds."""
        try:
            batches = await self.fetcher.fetch_unprocessed_batches()
        except Exception:
            logger.exception('detection cycle: fetch failed')   # NFR-03
            return

        if not batches:
            logger.info('detection cycle: no unprocessed events')
            return

        logger.info('detection cycle started', extra={'batches': len(batches)})
        for batch in batches:
            try:
                await self._process_batch(batch)
            except Exception:
                logger.exception('detection cycle: batch failed',
                                 extra={'contract': batch.get('contract_address')})

    async def _process_batch(self, batch: dict) -> None:
        contract = batch['contract_address']
        events = batch['events']
        event_ids = [e['id'] for e in events if e.get('id')]
        logger.info('processing batch', extra={'contract': contract[:16], 'events': len(events)})

        rule_alerts = []
        for rule in self.rules:
            try:
                alert = rule.evaluate(events)
            except Exception:
                logger.exception('rule failed', extra={'rule': rule.name})
                continue
            if alert:
                rule_alerts.append(alert)
                logger.info('rule fired', extra={'rule': rule.name, 'severity': alert.severity,
                                                 'anomaly_type': alert.anomaly_type})

        critical = [a for a in rule_alerts if a.severity == Severity.CRITICAL.value]
        if critical:
            for ra in critical:
                await self.writer.write_rule_alert(ra, contract, events)
            await self.writer.mark_processed(event_ids)
            return

        ai_batch = {
            'contract_address': contract,
            'time_window_seconds': batch.get('time_window_seconds', 60),
            'events': events,
            'rule_hints': [
                {'rule': a.rule_name, 'severity': a.severity,
                 'anomaly_type': a.anomaly_type, 'reason': a.reason}
                for a in rule_alerts
            ],
        }
        user_prompt = build_user_prompt(ai_batch)

        raw_response = await self.elfa.detect(SYSTEM_PROMPT, user_prompt)
        if raw_response is None:
            logger.info('elfa unavailable; trying altllm fallback')
            raw_response = await self.altllm.detect(SYSTEM_PROMPT, user_prompt)

        ai_result = parse_ai_response(raw_response)
        if ai_result is None:
            logger.warning('AI unavailable/invalid; writing rule alerts only',
                           extra={'contract': contract[:16], 'rule_alerts': len(rule_alerts)})
            for ra in rule_alerts:
                await self.writer.write_rule_alert(ra, contract, events)
        else:
            await self.writer.write_ai_alert(ai_result, contract, events, rule_alerts)

        await self.writer.log_detection(
            contract=contract, prompt=user_prompt, response=str(raw_response),
            event_ids=event_ids,
        )
        await self.writer.mark_processed(event_ids)
