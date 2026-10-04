import logging

import requests

from firstlight import config

logger = logging.getLogger(__name__)


def send_push(title: str, body: str, items: list[dict] | None = None) -> bool:
    """Send a POST to Simplepush with title and body."""
    key = getattr(config, "SIMPLEPUSH_KEY", None)
    if not key:
        logger.warning("SIMPLEPUSH_KEY not set in config/env. Skipping push.")
        return False

    url = "https://api.simplepush.io/send"
    public_url = getattr(config, "PUBLIC_URL", "")

    # Append the link to the full brief
    if public_url:
        body += f"\n\nRead full brief: {public_url}/brief"

    payload = {"key": key, "title": title, "msg": body}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send push notification: {e}")
        return False
