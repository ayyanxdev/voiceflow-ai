"""Demo webhook payloads for testing."""

from typing import Any


def generate_retell_call_started(call_id: str = "demo_retell_001", phone: str = "+15550101234") -> dict[str, Any]:
    return {
        "event": "call_started",
        "call": {
            "call_id": call_id,
            "direction": "inbound",
            "caller_number": phone,
            "agent_id": "agent_demo_001",
        },
    }


def generate_retell_call_ended(
    call_id: str = "demo_retell_001",
    phone: str = "+15550101234",
    duration_ms: int = 120000,
) -> dict[str, Any]:
    return {
        "event": "call_ended",
        "call": {
            "call_id": call_id,
            "direction": "inbound",
            "caller_number": phone,
            "duration_ms": duration_ms,
            "recording_url": f"https://storage.example.com/recordings/{call_id}.wav",
        },
    }


def generate_vapi_call_started(call_id: str = "demo_vapi_001") -> dict[str, Any]:
    return {
        "message": {
            "type": "call_started",
            "call": {
                "id": call_id,
                "direction": "outbound",
                "phone_number": "+15550202345",
            },
        },
    }


def generate_vapi_end_of_call(
    call_id: str = "demo_vapi_001",
    transcript: str = "AI: Hello! Welcome to Elite Roofing. How can I help you today?\nCaller: Hi, I need a roof inspection.\nAI: I'd be happy to help! Can I get your name?",
) -> dict[str, Any]:
    return {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": call_id,
                "direction": "outbound",
                "duration": 180,
                "transcript": transcript,
                "recording_url": f"https://storage.example.com/recordings/{call_id}.wav",
            },
            "analysis": {
                "summary": "Customer expressed interest in roof inspection. Lead qualified.",
                "sentiment": "positive",
                "call_successful": True,
            },
        },
    }
