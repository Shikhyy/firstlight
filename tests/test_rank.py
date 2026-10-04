from datetime import datetime, timedelta, timezone

from firstlight.pipeline.rank import compute_score, compute_urgency


def test_urgency():
    now = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)

    # Within 6 hours
    d1 = now + timedelta(hours=4)
    score, text = compute_urgency(d1.isoformat(), now)
    assert score == 1.0
    assert text == "closes in 4h"

    # Past
    d_past = now - timedelta(hours=1)
    score, text = compute_urgency(d_past.isoformat(), now)
    assert score == -1.0


def test_compute_score():
    s = compute_score(1.0, 1.0, 1.0, 1.0, 1.0)
    assert s == 1.0
