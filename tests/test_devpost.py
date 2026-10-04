from pathlib import Path

from firstlight.connectors.hackathons.devpost import DevpostConnector


def test_devpost_connector():
    fixture_path = Path(__file__).parent / "fixtures" / "devpost.json"

    connector = DevpostConnector()
    connector.url_override = f"file://{fixture_path.absolute()}"

    items = connector.fetch()

    assert len(items) > 0
    assert items[0].source == "devpost"

    paypal = next((i for i in items if "PayPal" in i.title), None)
    if paypal:
        assert "Nov 12, 2026" in paypal.deadline_text
