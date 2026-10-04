from firstlight.delivery.webpush import send_push


def test_webpush_stub(monkeypatch):
    import os

    monkeypatch.setattr(os.path, "exists", lambda x: False)
    res = send_push("Test", "Test body")
    # Returns False when VAPID keys are missing
    assert res is False
