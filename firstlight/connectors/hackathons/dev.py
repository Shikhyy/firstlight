import requests

from firstlight.connectors.base import Connector, RawItem


class DevChallengesConnector(Connector):
    name = "dev"

    def fetch(self) -> list[RawItem]:
        # Filter articles by devteam that mention challenge
        url = "https://dev.to/api/articles?username=devteam&per_page=30"

        # Test fixture handling
        if hasattr(self, "url_override"):
            url = self.url_override

        if url.startswith("file://"):
            import json

            path = url.replace("file://", "")
            with open(path, "r") as f:
                data = json.load(f)
        else:
            headers = {"User-Agent": "FirstLight/1.0"}
            resp = requests.get(url, headers=headers, timeout=self.timeout_s)
            resp.raise_for_status()
            data = resp.json()

        items = []
        for article in data:
            title = article.get("title", "")
            if "challenge" in title.lower() or "hackathon" in title.lower():
                # We skip "Congrats to the... Winners"
                if "winner" in title.lower() or "congrats" in title.lower():
                    continue

                items.append(
                    RawItem(
                        source=self.name,
                        title=title,
                        url=article.get("url", ""),
                        raw=article,
                        description=article.get("description", ""),
                        start_text=article.get("published_at"),
                    )
                )

        return items
