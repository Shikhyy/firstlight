from datetime import datetime, timezone

from dateutil.parser import parse as parse_date


def compute_urgency(
    deadline_iso: str | None, now_utc: datetime | None = None
) -> tuple[float, str]:
    if not deadline_iso:
        return 0.1, ""

    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    try:
        dt = parse_date(deadline_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except Exception:  # noqa: BLE001
        return 0.1, ""

    diff = dt - now_utc
    hours = diff.total_seconds() / 3600.0

    if hours < 0:
        return -1.0, "Ended"  # excluded

    days = hours / 24.0

    if hours <= 6:
        score = 1.0
        text = f"closes in {int(hours)}h" if hours >= 1 else "closes in <1h"
    elif hours <= 24:
        score = 0.85
        text = f"closes in {int(hours)}h"
    elif days <= 3:
        score = 0.6
        text = f"closes in {int(days)} days"
    elif days <= 7:
        score = 0.35
        text = f"closes in {int(days)} days"
    else:
        score = 0.1
        text = f"closes in {int(days)} days"

    return score, text


def compute_score(
    urgency: float,
    relevance: float = 1.0,
    eligibility: float = 1.0,
    effort_reward: float = 0.5,
    novelty: float = 1.0,
) -> float:
    if urgency < 0:
        return -1.0  # excluded

    return (
        0.40 * urgency
        + 0.30 * relevance
        + 0.15 * eligibility
        + 0.10 * effort_reward
        + 0.05 * novelty
    )
