import requests

from firstlight.connectors.base import Connector, RawItem


class DevpostConnector(Connector):
    name = "devpost"

    def fetch(self) -> list[RawItem]:
        url = "https://devpost.com/api/hackathons"

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
        hackathons = data.get("hackathons", [])

        for h in hackathons:
            title = h.get("title", "")
            url = h.get("url", "")

            # Parse dates "Oct 01 - Nov 12, 2026"
            deadline = None
            dates_str = h.get("submission_period_dates", "")
            if "-" in dates_str:
                parts = dates_str.split("-")
                end_str = parts[-1].strip()
                # end_str might be "Nov 12, 2026"
                deadline = end_str

            items.append(
                RawItem(
                    source=self.name,
                    title=title,
                    url=url,
                    raw=h,
                    deadline_text=deadline,
                )
            )

        return items
