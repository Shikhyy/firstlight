import requests
from pydantic import BaseModel

from firstlight import config


class VerdictSchema(BaseModel):
    should_enter: bool
    reason: str
    domains: list[str]


def get_verdict(title: str, description: str) -> str:
    """Uses LLM to decide if the user should enter and to extract left-over domains. Returns JSON string."""
    profile = config.PROFILE
    interests = ", ".join(profile.get("interests", []))
    name = profile.get("name", "User")

    sys_prompt = "You are FirstLight AI. Return ONLY valid JSON matching the schema."

    prompt = f"""
Event: {title}
Description: {description}

The user {name} likes: {interests}.
Are they a good fit? Provide a reason. Also provide a list of domains (like AI, web, mobile, security, opensource).
Respond as JSON:
{{
  "should_enter": true,
  "reason": "Brief reason...",
  "domains": ["ai", "web"]
}}
"""
    try:
        url = f"{config.OLLAMA_URL}/api/chat"
        payload = {
            "model": config.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": VerdictSchema.model_json_schema(),
        }
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")

        # Validate and return
        VerdictSchema.model_validate_json(content)
        return content
    except Exception:  # noqa: BLE001
        return '{"should_enter": false, "reason": "Failed to evaluate", "domains": []}'
