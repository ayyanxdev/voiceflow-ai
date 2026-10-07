"""Voice provider abstraction layer."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class VoiceProvider(ABC):
    """Abstract base class for voice providers (Retell, Vapi, etc.)."""

    @abstractmethod
    async def start_call(self, phone_number: str, agent_id: Optional[str] = None) -> dict:
        """Start an outbound call."""
        ...

    @abstractmethod
    async def end_call(self, call_id: str) -> dict:
        """End an active call."""
        ...

    @abstractmethod
    async def get_call(self, call_id: str) -> dict:
        """Get call details."""
        ...

    @abstractmethod
    def process_webhook(self, payload: dict) -> dict:
        """Process an incoming webhook event. Returns normalized event."""
        ...


class MockVoiceProvider(VoiceProvider):
    """Mock voice provider for demo mode."""

    def __init__(self):
        self._call_counter = 0

    async def start_call(self, phone_number: str, agent_id: Optional[str] = None) -> dict:
        self._call_counter += 1
        return {
            "call_id": f"mock_call_{self._call_counter}",
            "status": "initiated",
            "phone_number": phone_number,
        }

    async def end_call(self, call_id: str) -> dict:
        return {"call_id": call_id, "status": "completed"}

    async def get_call(self, call_id: str) -> dict:
        return {"call_id": call_id, "status": "completed", "duration": 120}

    def process_webhook(self, payload: dict) -> dict:
        return {
            "event_type": payload.get("event", "unknown"),
            "call_id": payload.get("call_id", "mock"),
            "data": payload,
        }
