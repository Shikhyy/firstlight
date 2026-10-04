import logging
from datetime import datetime, timezone

from firstlight.connectors.base import Connector, RawItem
from firstlight.db import get_connection

logger = logging.getLogger(__name__)


def fetch_safely(connector: Connector) -> list[RawItem]:
    """
    Executes connector.fetch(), catching all exceptions.
    Logs the result to the source_runs table.
    """
    start = datetime.now(timezone.utc)
    items = []
    ok = 1
    error_msg = None

    try:
        items = connector.fetch()
    except Exception as e:  # noqa: BLE001
        ok = 0
        error_msg = str(e)
        logger.error(f"Connector {connector.name} failed: {e}")

    end = datetime.now(timezone.utc)

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO source_runs (source, started_at, finished_at, ok, items_found, error) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    connector.name,
                    start.isoformat(),
                    end.isoformat(),
                    ok,
                    len(items),
                    error_msg,
                ),
            )
            conn.commit()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to log source_run for {connector.name}: {e}")

    return items
