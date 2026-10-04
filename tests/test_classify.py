from firstlight.pipeline.classify import classify_keywords


def test_classify_keywords():
    doms = classify_keywords("Hacktoberfest 2026", "Open source celebration")
    assert "opensource" in doms

    doms = classify_keywords("AI Hackathon", "LLM based")
    assert "ai" in doms
