from pathlib import Path

from firstlight import config
from firstlight.connectors.todos_md import TodosConnector


def test_todos_connector():
    fixture_path = Path(__file__).parent / "fixtures" / "todos.md"
    # Monkeypatch config
    config.SOURCES["todos_file"] = str(fixture_path)

    connector = TodosConnector()
    items = connector.fetch()

    assert len(items) == 2
    assert items[0].title == "Buy milk"
    assert items[0].deadline_text is None

    assert items[1].title == "Finish hackathon"
    assert items[1].deadline_text == "2026-10-05"
