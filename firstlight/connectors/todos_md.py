import re
from pathlib import Path

from firstlight import config
from firstlight.connectors.base import Connector, RawItem


class TodosConnector(Connector):
    name = "todos"

    def fetch(self) -> list[RawItem]:
        todos_path = config.SOURCES.get("todos_file", "data/todos.md")
        p = Path(todos_path)
        if not p.exists():
            return []

        items = []
        with open(p, "r") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line.startswith(("- [ ]", "* [ ]")):
                    title = line[5:].strip()
                    # Check for due date like (due: 2026-10-05)
                    due = None
                    m = re.search(r"\(due:\s*([^)]+)\)", title)
                    if m:
                        due = m.group(1).strip()
                        title = title[: m.start()].strip()

                    items.append(
                        RawItem(
                            source=self.name,
                            title=title,
                            url=f"todo:{idx}",
                            raw={"line": line},
                            deadline_text=due,
                        )
                    )
        return items
