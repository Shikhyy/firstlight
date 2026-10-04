from firstlight.delivery.webpush import send_push


def test_webpush_stub():
    res = send_push("Test", "Test body")
    assert res is True
