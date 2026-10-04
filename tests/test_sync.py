import firstlight.db
from firstlight.connectors.base import RawItem
from firstlight.db import get_connection, init_db
from firstlight.pipeline.sync import sync_items


def test_sync_items(tmp_path):
    firstlight.db.DB_PATH = tmp_path / "test.db"
    init_db()

    items = [
        RawItem(
            source="rss",
            title="News",
            url="http://n.com",
            raw={"published": "2026-10-01"},
        ),
        RawItem(
            source="devpost",
            title="Hack",
            url="http://h.com",
            raw={"x": 1},
            deadline_text="2026-11-01",
        ),
        RawItem(
            source="todos",
            title="Buy milk",
            url="Buy milk",
            raw={},
            deadline_text="2026-10-05",
        ),
        RawItem(
            source="calendar",
            title="Meeting",
            url="uid123",
            raw={},
            start_text="2026-10-04T10:00:00",
        ),
    ]

    sync_items(items)

    with get_connection() as conn:
        assert conn.execute("SELECT count(*) FROM news_items").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM events").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM event_sources").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM todos").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM calendar_items").fetchone()[0] == 1

        # Test upsert
        sync_items(items)
        assert conn.execute("SELECT count(*) FROM events").fetchone()[0] == 1
