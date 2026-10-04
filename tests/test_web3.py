from pathlib import Path

from firstlight.connectors.hackathons.web3 import Web3Connector


def test_web3_connector():
    fixture_path = Path(__file__).parent / "fixtures" / "web3.json"

    connector = Web3Connector()
    connector.url_override = f"file://{fixture_path.absolute()}"

    items = connector.fetch()
    assert len(items) == 1
    assert items[0].source == "web3"
    assert "2026-10-30" in items[0].deadline_text
