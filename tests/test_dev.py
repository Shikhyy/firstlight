from pathlib import Path

from firstlight.connectors.hackathons.dev import DevChallengesConnector


def test_dev_connector(monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "dev_articles.json"

    connector = DevChallengesConnector()
    connector.url_override = f"file://{fixture_path.absolute()}"

    items = connector.fetch()

    # We should have one challenge item
    # "Join the Hacktoberfest Weekend Challenge..."
    # "Hacktoberfest 2026 DEV Challenges: Five Challenges..."

    assert len(items) > 0
    assert any("DEV Challenges" in i.title for i in items)
    assert items[0].source == "dev"
    assert items[0].url.startswith("https://dev.to/")
