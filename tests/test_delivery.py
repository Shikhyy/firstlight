import requests_mock

from firstlight.delivery.ntfy import send_ntfy_push


def test_ntfy_push():
    with requests_mock.Mocker() as m:
        m.post("https://ntfy.sh/default-topic", text="ok")
        success = send_ntfy_push("Test Title", "Test Body")
        assert success is True

        request = m.last_request
        assert request.headers["Title"] == "Test Title"
        assert request.headers["Click"] == "http://localhost:5000/brief"
        assert "view, Open, http://localhost:5000/brief" in request.headers["Actions"]
        assert request.text == "Test Body"
