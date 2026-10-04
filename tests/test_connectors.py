from pathlib import Path

from firstlight.connectors.rss_news import RssConnector


def test_rss_connector_parses_fixture():
    fixture_path = Path(__file__).parent / "fixtures" / "rss.xml"
    url = f"file://{fixture_path.absolute()}"
    connector = RssConnector(urls=[url])
    items = connector.fetch()

    assert len(items) == 2
    assert items[0].title == "Gemma 3 released!"
    assert items[0].url == "https://example.com/gemma-3"
    assert items[0].description == "Google releases Gemma 3 open weights."
    assert items[0].source == "rss"
