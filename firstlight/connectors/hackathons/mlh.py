import requests

from firstlight.connectors.base import Connector, RawItem


class MlhConnector(Connector):
    name = "mlh"

    def fetch(self) -> list[RawItem]:
        url = "https://mlh.io/events.json"  # dummy endpoint
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
        for h in data:
            items.append(
                RawItem(
                    source=self.name,
                    title=h.get("name", ""),
                    url=h.get("url", ""),
                    raw=h,
                    deadline_text=h.get("end_date"),
                )
            )
        return items
