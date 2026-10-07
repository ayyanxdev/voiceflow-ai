"""Retell AI integration."""

from typing import Any, Optional

from app.integrations.voice_provider import VoiceProvider


class RetellProvider(VoiceProvider):
    """
    Retell AI voice provider.

    Requires RETELL_API_KEY to be configured.
    Falls back to mock behavior when not configured.
    """

    def __init__(self, api_key: Optional[str] = None, agent_id: Optional[str] = None):
        self.api_key = api_key
        self.agent_id = agent_id
        self._available = bool(api_key)

    @property
    def is_available(self) -> bool:
        return self._available

    async def start_call(self, phone_number: str, agent_id: Optional[str] = None) -> dict:
        if not self._available:
            return {"call_id": "retell_mock", "status": "mock_mode", "phone_number": phone_number}

        # Real implementation would use Retell SDK/API
        # import retellai
        # client = retellai.Retell(api_key=self.api_key)
        # call = client.call phoneNumber=phone_number, fromNumber=..., agentId=agent_id or self.agent_id
        raise NotImplementedError("Retell API integration requires API key configuration")

    async def end_call(self, call_id: str) -> dict:
        if not self._available:
            return {"call_id": call_id, "status": "mock_completed"}
        raise NotImplementedError("Retell API integration requires API key configuration")

    async def get_call(self, call_id: str) -> dict:
        if not self._available:
            return {"call_id": call_id, "status": "mock_completed"}
        raise NotImplementedError("Retell API integration requires API key configuration")

    def process_webhook(self, payload: dict) -> dict:
        """
        Process Retell webhook events.

        Retell sends events like:
        - call_started
        - call_ended
        - call_analyzed
        """
        event_type = payload.get("event", "unknown")

        call_data = payload.get("call", {})

        # Normalize Retell event to our format
        normalized = {
            "provider": "retell",
            "event_type": event_type,
            "call_id": call_data.get("call_id") or payload.get("call_id"),
            "external_id": call_data.get("call_id"),
            "status": None,
            "outcome": None,
            "transcript": None,
            "summary": None,
            "duration_seconds": 0,
            "recording_url": None,
            "sentiment": None,
            "direction": "inbound" if call_data.get("direction") == "inbound" else "outbound",
            # Contact info — needed for lead creation/matching
            "phone": call_data.get("caller_number"),
            "caller_name": call_data.get("caller_name"),
            "email": call_data.get("caller_email"),
        }

        if event_type == "call_started":
            normalized["status"] = "answered"
        elif event_type == "call_ended":
            normalized["status"] = "completed"
            normalized["duration_seconds"] = call_data.get("duration_ms", 0) // 1000
            normalized["recording_url"] = call_data.get("recording_url")
            # Retell may include transcript in call_ended
            if call_data.get("transcript"):
                normalized["transcript"] = call_data["transcript"]
        elif event_type == "call_analyzed":
            normalized["summary"] = call_data.get("call_analysis", {}).get("summary")
            normalized["transcript"] = call_data.get("transcript")
            analysis = call_data.get("call_analysis", {})
            if analysis.get("call_successful"):
                normalized["outcome"] = "qualified"
            else:
                normalized["outcome"] = "other"
            # Some Retell setups put transcript at the top level
            if not normalized["transcript"]:
                normalized["transcript"] = payload.get("call", {}).get("transcript")

        return normalized
