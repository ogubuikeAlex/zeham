import json
import logging

import httpx

logger = logging.getLogger(__name__)


async def chat_json(
    *, provider: str, base_url: str, api_key: str, model: str,
    system_prompt: str, user_prompt: str, timeout: float,
) -> dict | None:
    """POST a chat completion and json.loads() the assistant message. None on any failure."""
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.1,   # deterministic-ish output
        'max_tokens': 512,
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            resp = await client.post(f'{base_url}/chat/completions', json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data['choices'][0]['message']['content'].strip()
            logger.debug('%s raw response', provider, extra={'preview': raw_text[:200]})
            # Tolerate a ```json fence if the model adds one despite instructions.
            if raw_text.startswith('```'):
                raw_text = raw_text.strip('`')
                raw_text = raw_text[4:] if raw_text.lower().startswith('json') else raw_text
                raw_text = raw_text.strip()
            return json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.warning('%s returned non-JSON', provider, extra={'error': str(e)})
        return None
    except Exception as e:
        logger.warning('%s call failed', provider, extra={'error': str(e)})
        return None
