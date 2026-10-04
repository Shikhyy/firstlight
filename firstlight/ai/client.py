import json
import logging

import requests

from firstlight import config
from firstlight.ai.schemas import BriefSummary

logger = logging.getLogger(__name__)


def call_ollama(system_prompt: str, user_prompt: str) -> BriefSummary | None:
    timeout_s = config.AI_CONFIG.get("timeout_s", 60)

    # Check for Groq API fallback in config
    import os

    import yaml

    groq_key = None
    hf_token = None
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
            groq_key = cfg.get("integrations", {}).get("groq_api_key")
            hf_token = cfg.get("integrations", {}).get("hf_token")

    if groq_key:
        return _call_groq(groq_key, system_prompt, user_prompt, timeout_s)
    if hf_token:
        return _call_hf(hf_token, system_prompt, user_prompt, timeout_s)

    # Local Ollama fallback
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": BriefSummary.model_json_schema(),
    }

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


def _call_groq(
    api_key: str, system_prompt: str, user_prompt: str, timeout_s: int
) -> BriefSummary | None:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gemma2-9b-it",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout_s,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return BriefSummary.model_validate_json(content)
    except Exception as e:  # noqa: BLE001
        logger.error(f"Groq cloud fallback failed: {e}")
        return None


def _call_hf(
    api_key: str, system_prompt: str, user_prompt: str, timeout_s: int
) -> BriefSummary | None:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemma-2-2b-it",
        "messages": [{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}],
        "max_tokens": 1000,
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/gemma-2-2b-it/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout_s,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        content = content.removeprefix("```json")
        content = content.removesuffix("```")
        content = content.strip()
        return BriefSummary.model_validate_json(content)
    except Exception as e:  # noqa: BLE001
        logger.error(f"Hugging Face cloud fallback failed: {e}")
        return None
