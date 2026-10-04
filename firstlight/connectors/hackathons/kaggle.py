import requests

from firstlight.connectors.base import Connector, RawItem


class KaggleConnector(Connector):
    name = "kaggle"

    def fetch(self) -> list[RawItem]:
        url = "https://www.kaggle.com/api/v1/competitions/list"
        if hasattr(self, "url_override"):
            url = self.url_override

        if url.startswith("file://"):
            import json

            path = url.replace("file://", "")
            with open(path, "r") as f:
                data = json.load(f)
        else:
            # We would use HTTPBasicAuth with KAGGLE_USERNAME and KAGGLE_KEY here
            headers = {"User-Agent": "FirstLight/1.0"}
            resp = requests.get(url, headers=headers, timeout=self.timeout_s)
            resp.raise_for_status()
            data = resp.json()

        items = []
        for c in data:
            items.append(
                RawItem(
                    source=self.name,
                    title=c.get("title", ""),
                    url=c.get("url", ""),
                    raw=c,
                    deadline_text=c.get("deadline"),
                )
            )
        return items
