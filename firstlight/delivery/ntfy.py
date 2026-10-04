import logging

import requests

from firstlight import config

logger = logging.getLogger(__name__)


def send_ntfy_push(title: str, body: str, items: list[dict] | None = None) -> bool:
    """Send one POST to the ntfy topic with title, body, click URL and action buttons."""
    topic = config.NTFY_TOPIC
    url = f"{config.NTFY_BASE_URL}/{topic}"
    public_url = config.PUBLIC_URL
    token = config.ACTION_TOKEN

    actions = []
    # If items provided, add a sample Done/Snooze for the top item (or based on some logic)
    # The requirement says: Actions: Done, Snooze 1h, Open
    # For Phase 1 skeleton, we can just hardcode a dummy or skip if no specific item.
    if items and items[0].get("ref", "").startswith("todo:"):
        todo_id = items[0]["ref"].split(":")[-1]
        actions.append(
            f"http, Done, {public_url}/api/todos/{todo_id}/done?token={token}, method=POST"
        )
        actions.append(
            f"http, Snooze 1h, {public_url}/api/todos/{todo_id}/snooze?token={token}, method=POST"
        )

    actions.append(f"view, Open, {public_url}/brief")

    headers = {
        "Title": title,
        "Click": f"{public_url}/brief",
        "Actions": "; ".join(actions),
    }

    try:
        resp = requests.post(
            url, data=body.encode("utf-8"), headers=headers, timeout=10
        )
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send ntfy push: {e}")
        return False
