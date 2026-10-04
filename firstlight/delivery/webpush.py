import json
import logging
import os

from pywebpush import WebPushException, webpush

from firstlight.db import get_connection

logger = logging.getLogger(__name__)


def send_push(title: str, body: str, items: list[dict] | None = None) -> bool:
    """Send Web Push to all active subscriptions."""
    vapid_file = os.path.join("data", "vapid.json")
    if not os.path.exists(vapid_file):
        logger.error("VAPID keys not found. Run generate_vapid.py.")
        return False

    with open(vapid_file) as f:
        vapid_data = json.load(f)

    private_key = vapid_data["private_key"]

    payload = json.dumps({"title": title, "body": body, "url": "/brief"})

    success = False
    with get_connection() as conn:
        subs = conn.execute("SELECT * FROM webpush_subscriptions").fetchall()
        for sub in subs:
            try:
                sub_info = json.loads(sub["subscription_json"])
                webpush(
                    subscription_info=sub_info,
                    data=payload,
                    vapid_private_key=private_key,
                    vapid_claims={"sub": "mailto:shikhar@example.com"},
                )
                success = True
            except WebPushException as ex:
                logger.error(f"Web Push failed: {ex}")
                # Optional: Delete subscription on 410 Gone
                if ex.response and ex.response.status_code == 410:
                    conn.execute(
                        "DELETE FROM webpush_subscriptions WHERE id = ?", (sub["id"],)
                    )
                    conn.commit()
            except Exception as e:  # noqa: BLE001
                logger.error(f"Unknown web push error: {e}")

    return success
