import json

import requests_mock

from firstlight.ai.client import call_ollama


def test_ollama_valid_json():
    with requests_mock.Mocker() as m:
        mock_resp = {
            "message": {
                "content": json.dumps(
                    {
                        "title": "A busy day",
                        "quiet_day": False,
                        "items": [
                            {
                                "ref": "item:1",
                                "headline": "Gemma 3 out",
                                "why": "New model release.",
                            }
                        ],
                    }
                )
            }
        }
        m.post("http://localhost:11434/api/chat", json=mock_resp)
        summary = call_ollama("sys", "user")
        assert summary is not None
        assert summary.title == "A busy day"
        assert len(summary.items) == 1
        assert summary.items[0].headline == "Gemma 3 out"


def test_ollama_invalid_json():
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/chat", text="Not JSON")
        summary = call_ollama("sys", "user")
        assert summary is None


def test_ollama_timeout():
    with requests_mock.Mocker() as m:
        import requests

        m.post("http://localhost:11434/api/chat", exc=requests.exceptions.Timeout)
        summary = call_ollama("sys", "user")
        assert summary is None
