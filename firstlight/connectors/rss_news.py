import feedparser

from firstlight.connectors.base import Connector, RawItem


class RssConnector(Connector):
    name = "rss"

    def __init__(self, urls: list[str]):
        self.urls = urls

    def fetch(self) -> list[RawItem]:
        items = []
        import logging

        import requests

        logger = logging.getLogger(__name__)

        for url in self.urls:
            if url.startswith("file://"):
                feed = feedparser.parse(url)
            else:
                try:
                    # Use requests to bypass urllib SSL issues on this machine
                    resp = requests.get(url, timeout=self.timeout_s)
                    resp.raise_for_status()
                    feed = feedparser.parse(resp.content)
                except requests.RequestException as e:
                    logger.error(f"Network error fetching {url}: {e}")
                    continue

            if feed.bozo:
                # If parsing failed drastically, we could raise or log.
                # For now, we continue if there are entries.
                pass

            for entry in feed.entries:
                items.append(
                    RawItem(
                        source=self.name,
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        raw={"published": entry.get("published", "")},
                        description=entry.get("summary", ""),
                    )
                )
        return items
