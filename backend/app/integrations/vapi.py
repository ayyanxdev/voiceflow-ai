"""Vapi AI integration."""

from typing import Optional

from app.integrations.voice_provider import VoiceProvider


class VapiProvider(VoiceProvider):
    """
    Vapi AI voice provider.

    Requires VAPI_API_KEY to be configured.
    Falls back to mock behavior when not configured.
    """

    def __init__(self, api_key: Optional[str] = None, assistant_id: Optional[str] = None):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self._available = bool(api_key)

    @property
    def is_available(self) -> bool:
        return self._available

    async def start_call(self, phone_number: str, agent_id: Optional[str] = None) -> dict:
        if not self._available:
            return {"call_id": "vapi_mock", "status": "mock_mode", "phone_number": phone_number}
        raise NotImplementedError("Vapi API integration requires API key configuration")

    async def end_call(self, call_id: str) -> dict:
        if not self._available:
            return {"call_id": call_id, "status": "mock_completed"}
        raise NotImplementedError("Vapi API integration requires API key configuration")

    async def get_call(self, call_id: str) -> dict:
        if not self._available:
            return {"call_id": call_id, "status": "mock_completed"}
        raise NotImplementedError("Vapi API integration requires API key configuration")

    def process_webhook(self, payload: dict) -> dict:
        """
        Process Vapi webhook events.

        Vapi sends events like:
        - call_started
        - call_ended
        - call_updated
        - function-call
        - end-of-call-report
        """
        event_type = payload.get("message", {}).get("type") or payload.get("event", "unknown")
        call_data = payload.get("call", {}) or payload.get("message", {}).get("call", {})

        normalized = {
            "provider": "vapi",
            "event_type": event_type,
            "call_id": call_data.get("id"),
            "external_id": call_data.get("id"),
            "status": None,
            "outcome": None,
            "transcript": None,
            "summary": None,
            "duration_seconds": 0,
            "recording_url": None,
            "sentiment": None,
            "direction": call_data.get("direction", "outbound"),
        }

        if event_type == "call_started":
            normalized["status"] = "answered"
        elif event_type in ("call_ended", "end-of-call-report"):
            normalized["status"] = "completed"
            normalized["duration_seconds"] = call_data.get("duration", 0)

            # Extract transcript
            transcript_obj = call_data.get("transcript")
            if isinstance(transcript_obj, str):
                normalized["transcript"] = transcript_obj
            elif isinstance(transcript_obj, list):
                normalized["transcript"] = "\n".join(
                    f"{t.get('role', 'unknown')}: {t.get('content', '')}"
                    for t in transcript_obj
                )

            # Extract summary from end-of-call report
            summary_data = payload.get("message", {}).get("analysis", {})
            if summary_data:
                normalized["summary"] = summary_data.get("summary")
                normalized["sentiment"] = summary_data.get("sentiment")

            # Recording
            normalized["recording_url"] = call_data.get("recording_url")

        return normalized
