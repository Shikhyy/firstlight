from firstlight.pipeline.normalize import normalize_date


def test_normalize_date():
    iso, conf = normalize_date("2026-10-05T12:00:00Z")
    assert iso == "2026-10-05T12:00:00+00:00"
    assert conf == 1.0

    iso, conf = normalize_date("Jan 1 1999")
    assert conf == 0.1

    iso, conf = normalize_date("Not a date")
    assert iso is None
    assert conf == 0.0
