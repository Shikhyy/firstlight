from pathlib import Path

from firstlight.connectors.calendar_ics import CalendarConnector


def test_calendar_connector(monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "cal.ics"
    monkeypatch.setenv("ICS_URL", f"file://{fixture_path.absolute()}")

    connector = CalendarConnector()
    items = connector.fetch()

    assert len(items) == 1
    assert items[0].title == "Hackathon Kickoff"
    assert "2026-10-05" in items[0].start_text
