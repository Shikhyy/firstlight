import json
import logging
from datetime import datetime, timezone

from firstlight.connectors.base import RawItem
from firstlight.db import get_connection

logger = logging.getLogger(__name__)


def sync_items(items: list[RawItem]):
    """Syncs raw items to their respective tables based on their source."""
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        for item in items:
            try:
                if item.source == "rss":
                    _sync_news(conn, item, now_iso)
                elif item.source == "calendar":
                    _sync_calendar(conn, item)
                elif item.source == "todos":
                    _sync_todo(conn, item, now_iso)
                else:
                    # Hackathons go to events
                    _sync_event(conn, item, now_iso)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error syncing item {item.title}: {e}")
        conn.commit()


def _sync_news(conn, item: RawItem, now_iso: str):
    conn.execute(
        "INSERT INTO news_items (url, title, source, published_at, fetched_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(url) DO UPDATE SET fetched_at=excluded.fetched_at",
        (item.url, item.title, item.source, item.raw.get("published"), now_iso),
    )


def _sync_calendar(conn, item: RawItem):
    # calendar sets URL to uid
    conn.execute(
        "INSERT INTO calendar_items (uid, title, start_at, end_at, location) VALUES (?, ?, ?, ?, ?) ON CONFLICT(uid) DO UPDATE SET title=excluded.title, start_at=excluded.start_at",
        (item.url, item.title, item.start_text, item.deadline_text, None),
    )


def _sync_todo(conn, item: RawItem, now_iso: str):
    # Todo connector returns url as the line title.
    # We will use title as unique for now, though it's not strictly unique in schema (we don't have unique constraint on title)
    # Actually schema has no unique on todos. We just insert if it doesn't exist.
    # To prevent duplicates, we can check by title.
    existing = conn.execute(
        "SELECT id FROM todos WHERE title = ?", (item.title,)
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO todos (title, due_at, source, created_at) VALUES (?, ?, ?, ?)",
            (item.title, item.deadline_text, item.source, now_iso),
        )


def _sync_event(conn, item: RawItem, now_iso: str):
    from firstlight.pipeline.dedupe import canonicalize_url

    c_url = canonicalize_url(item.url)
    if not c_url:
        return

    # Check if we have an event for this canonical_key
    row = conn.execute(
        "SELECT id FROM events WHERE canonical_key = ?", (c_url,)
    ).fetchone()

    if not row:
        cursor = conn.execute(
            """INSERT INTO events (canonical_key, title, description, deadline_at, status, first_seen, last_seen)
               VALUES (?, ?, ?, ?, 'open', ?, ?)""",
            (c_url, item.title, item.description, item.deadline_text, now_iso, now_iso),
        )
        event_id = cursor.lastrowid
    else:
        event_id = row["id"]
        conn.execute(
            "UPDATE events SET last_seen = ?, title = ?, description = ?, deadline_at = ? WHERE id = ?",
            (now_iso, item.title, item.description, item.deadline_text, event_id),
        )

    # Upsert source
    conn.execute(
        """INSERT INTO event_sources (event_id, platform, url, raw_json, fetched_at)
           VALUES (?, ?, ?, ?, ?) ON CONFLICT(platform, url) DO UPDATE SET fetched_at=excluded.fetched_at, raw_json=excluded.raw_json""",
        (event_id, item.source, item.url, json.dumps(item.raw), now_iso),
    )
