from firstlight.pipeline.verdict import get_verdict


def test_get_verdict(requests_mock):
    requests_mock.post(
        "http://localhost:11434/api/chat",
        json={
            "message": {
                "content": '{"should_enter": true, "reason": "Cool", "domains": ["ai"]}'
            }
        },
    )

    res = get_verdict("AI Hackathon", "Build with LLMs")
    assert "true" in res
    assert "Cool" in res
    assert "ai" in res
