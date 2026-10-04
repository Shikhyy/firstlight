from pathlib import Path

from firstlight.connectors.hackathons.kaggle import KaggleConnector


def test_kaggle_connector():
    fixture_path = Path(__file__).parent / "fixtures" / "kaggle.json"

    connector = KaggleConnector()
    connector.url_override = f"file://{fixture_path.absolute()}"

    items = connector.fetch()
    assert len(items) == 1
    assert items[0].source == "kaggle"
    assert "2026-12-31" in items[0].deadline_text
