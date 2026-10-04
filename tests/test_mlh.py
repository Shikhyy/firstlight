from pathlib import Path

from firstlight.connectors.hackathons.mlh import MlhConnector


def test_mlh_connector():
    fixture_path = Path(__file__).parent / "fixtures" / "mlh.json"

    connector = MlhConnector()
    connector.url_override = f"file://{fixture_path.absolute()}"

    items = connector.fetch()
    assert len(items) == 1
    assert items[0].source == "mlh"
    assert items[0].deadline_text == "2026-10-12"
