from firstlight.db import init_db
from firstlight.pipeline.seen import is_novel, mark_seen


def test_seen_items(tmp_path):
    import firstlight.db

    firstlight.db.DB_PATH = tmp_path / "test.db"
    init_db()

    assert is_novel("event", "123") is True
    mark_seen("event", "123")
    assert is_novel("event", "123") is False
    assert is_novel("event", "456") is True
