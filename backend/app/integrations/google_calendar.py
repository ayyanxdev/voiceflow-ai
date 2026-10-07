"""Google Calendar integration abstraction."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional


class CalendarProvider(ABC):
    """Abstract calendar provider interface."""

    @abstractmethod
    async def create_event(
        self, title: str, start_time: datetime, end_time: Optional[datetime] = None,
        description: str = "", attendee_email: Optional[str] = None,
    ) -> dict:
        ...

    @abstractmethod
    async def update_event(self, event_id: str, **kwargs) -> dict:
        ...

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        ...

    @abstractmethod
    async def list_events(
        self, start: datetime, end: datetime
    ) -> list[dict]:
        ...


class MockCalendarProvider(CalendarProvider):
    """Mock calendar provider for demo mode."""

    def __init__(self):
        self._events: dict[str, dict] = {}
        self._counter = 0

    async def create_event(
        self, title: str, start_time: datetime, end_time: Optional[datetime] = None,
        description: str = "", attendee_email: Optional[str] = None,
    ) -> dict:
        self._counter += 1
        event_id = f"mock_event_{self._counter}"
        event = {
            "id": event_id,
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": (end_time or start_time).isoformat(),
            "description": description,
            "attendee_email": attendee_email,
        }
        self._events[event_id] = event
        return event

    async def update_event(self, event_id: str, **kwargs) -> dict:
        event = self._events.get(event_id, {})
        event.update(kwargs)
        self._events[event_id] = event
        return event

    async def delete_event(self, event_id: str) -> bool:
        if event_id in self._events:
            del self._events[event_id]
            return True
        return False

    async def list_events(self, start: datetime, end: datetime) -> list[dict]:
        return list(self._events.values())


class GoogleCalendarProvider(CalendarProvider):
    """
    Google Calendar integration.

    Requires GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_CALENDAR_ID.
    """

    def __init__(self, client_id: str, client_secret: str, calendar_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.calendar_id = calendar_id

    async def create_event(self, title, start_time, end_time=None, description="", attendee_email=None):
        raise NotImplementedError("Google Calendar requires OAuth credentials")

    async def update_event(self, event_id, **kwargs):
        raise NotImplementedError("Google Calendar requires OAuth credentials")

    async def delete_event(self, event_id):
        raise NotImplementedError("Google Calendar requires OAuth credentials")

    async def list_events(self, start, end):
        raise NotImplementedError("Google Calendar requires OAuth credentials")
