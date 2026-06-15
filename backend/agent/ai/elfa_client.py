import logging

from config import settings
from .openai_compat import chat_json

logger = logging.getLogger(__name__)


class ElfaClient:
    name = 'elfa'

    def __init__(self):
        self.base_url = settings.elfa_base_url
        self.model = settings.elfa_model
        self.api_key = settings.elfa_api_key

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def detect(self, system_prompt: str, user_prompt: str) -> dict | None:
        if not self.enabled:
            logger.info('elfa disabled (no ELFA_API_KEY); skipping')
            return None
        return await chat_json(
            provider=self.name, base_url=self.base_url, api_key=self.api_key,
            model=self.model, system_prompt=system_prompt, user_prompt=user_prompt,
            timeout=settings.ai_timeout_seconds,
        )
