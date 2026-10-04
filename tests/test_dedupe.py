from firstlight.pipeline.dedupe import canonicalize_url, deduplicate_events


def test_canonicalize_url():
    url1 = "https://example.com/hackathon/?utm_source=twitter"
    url2 = "http://EXAMPLE.com/hackathon"
    assert canonicalize_url(url1) == canonicalize_url(url2)


def test_deduplicate_events():
    events = [
        {"title": "Global Hack 2026", "url": "https://hack.com", "source": "devpost"},
        {"title": "Global Hack 2026!", "url": "https://other.com", "source": "mlh"},
        {"title": "Something else", "url": "https://hack.com", "source": "dev"},
    ]

    res = deduplicate_events(events)
    # 1 and 3 merge on URL.
    # 1 and 2 merge on fuzzy title.
    # Total should be 1 item.
    assert len(res) == 1
    assert "devpost" in res[0]["source"]
    assert "mlh" in res[0]["source"]
    assert "dev" in res[0]["source"]
