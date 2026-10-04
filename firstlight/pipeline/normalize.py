import logging
from datetime import timezone

from dateutil.parser import parse as parse_date

logger = logging.getLogger(__name__)


def normalize_date(date_text: str | None) -> tuple[str | None, float]:
    """
    Parses date_text to ISO 8601 UTC string.
    Returns (iso_string, confidence).
    """
    if not date_text:
        return None, 0.0

    try:
        dt = parse_date(date_text, fuzzy=True)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        # Plausibility check
        if dt.year < 2000 or dt.year > 2100:
            return dt.isoformat(), 0.1

        return dt.isoformat(), 1.0
    except (ValueError, OverflowError, TypeError) as e:
        logger.warning(f"Failed to parse date '{date_text}': {e}")
        return None, 0.0
