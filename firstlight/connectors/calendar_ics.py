import os

import requests
from icalendar import Calendar

from firstlight.connectors.base import Connector, RawItem


class CalendarConnector(Connector):
    name = "calendar"

    def fetch(self) -> list[RawItem]:
        ics_url = os.environ.get("ICS_URL")
        if not ics_url:
            return []

        try:
            if ics_url.startswith("file://"):
                path = ics_url.replace("file://", "")
                with open(path, "rb") as f:
                    content = f.read()
            else:
                resp = requests.get(ics_url, timeout=self.timeout_s)
                resp.raise_for_status()
                content = resp.content

            cal = Calendar.from_ical(content)
        except Exception:  # noqa: BLE001
            return []

        items = []
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get("summary", ""))
                dtstart = component.get("dtstart")
                dtstart_val = dtstart.dt.isoformat() if hasattr(dtstart, "dt") else None

                items.append(
                    RawItem(
                        source=self.name,
                        title=summary,
                        url="",
                        raw={"uid": str(component.get("uid", ""))},
                        start_text=dtstart_val,
                    )
                )

        return items
