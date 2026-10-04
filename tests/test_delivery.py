import firstlight.config
from firstlight.delivery.simplepush import send_push


def test_send_push_success(requests_mock, monkeypatch):
    monkeypatch.setattr(firstlight.config, "SIMPLEPUSH_KEY", "test_key", raising=False)

    requests_mock.post("https://api.simplepush.io/send", text="OK")

    result = send_push("Test Title", "Test Body")
    assert result is True
    assert requests_mock.called


def test_send_push_missing_key(monkeypatch):
    monkeypatch.setattr(firstlight.config, "SIMPLEPUSH_KEY", "", raising=False)
    result = send_push("Test Title", "Test Body")
    assert result is False
