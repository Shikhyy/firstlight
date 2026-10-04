from datetime import datetime, timezone

from firstlight.db import get_connection


def is_novel(item_type: str, item_ref: str) -> bool:
    """Returns True if item was never seen, False otherwise."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT shown_at FROM seen_items WHERE item_type = ? AND item_ref = ?",
            (item_type, item_ref),
        ).fetchone()
        return row is None


def mark_seen(item_type: str, item_ref: str):
    """Marks an item as seen today."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_items (item_type, item_ref, shown_at) VALUES (?, ?, ?)",
            (item_type, item_ref, now),
        )
        conn.commit()
