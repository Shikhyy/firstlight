import json
import logging

import requests

from firstlight import config
from firstlight.ai.schemas import BriefSummary

logger = logging.getLogger(__name__)


def call_ollama(system_prompt: str, user_prompt: str) -> BriefSummary | None:
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": BriefSummary.model_json_schema(),
    }

    timeout_s = config.AI_CONFIG.get("timeout_s", 60)
    url = f"{config.OLLAMA_URL}/api/chat"

    try:
        response = requests.post(url, json=payload, timeout=timeout_s)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        # Parse and validate against schema
        summary = BriefSummary.model_validate_json(content)
        return summary
    except (requests.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Ollama call failed: {e}")
        return None
    except ValueError as e:
        logger.error(f"Ollama output validation failed: {e}")
        return None
