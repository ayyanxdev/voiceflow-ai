"""AI call summary service."""

import random
from typing import Any, Optional


def generate_mock_summary(transcript: str) -> dict[str, Any]:
    """Generate a mock AI summary from a transcript. Used in demo mode."""
    transcript_lower = (transcript or "").lower()

    appointment_requested = any(
        kw in transcript_lower
        for kw in ["appointment", "schedule", "book", "meeting", "come in"]
    )
    interested = any(
        kw in transcript_lower
        for kw in ["interested", "yes", "sure", "need", "want", "looking for"]
    )
    not_interested = any(
        kw in transcript_lower
        for kw in ["not interested", "no thanks", "no thank you", "don't need"]
    )

    if not_interested:
        score = random.randint(10, 30)
        interest_level = "low"
        next_action = "No follow-up needed"
    elif appointment_requested:
        score = random.randint(75, 98)
        interest_level = "high"
        next_action = "Confirm appointment and send reminder"
    elif interested:
        score = random.randint(50, 80)
        interest_level = "medium"
        next_action = "Follow up in 2-3 days"
    else:
        score = random.randint(20, 60)
        interest_level = "low"
        next_action = "Review transcript for follow-up opportunities"

    key_points = []
    if "roof" in transcript_lower:
        key_points.append("Customer mentioned roofing services")
    if "inspect" in transcript_lower:
        key_points.append("Customer interested in inspection")
    if "price" in transcript_lower or "cost" in transcript_lower:
        key_points.append("Customer asked about pricing")
    if "emergency" in transcript_lower:
        key_points.append("Urgent/emergency request")
    if "insurance" in transcript_lower:
        key_points.append("Insurance-related inquiry")

    if not key_points:
        key_points = ["Customer inquiry handled by AI agent"]

    return {
        "summary": (
            f"AI agent handled the call successfully. "
            f"{'Customer expressed interest and ' if interested else ''}"
            f"{'requested an appointment.' if appointment_requested else 'Information was provided.'}"
        ),
        "customer_intent": "service_inquiry",
        "interest_level": interest_level,
        "qualification_score": score,
        "key_points": key_points,
        "objections": ["pricing concerns"] if "price" in transcript_lower else [],
        "next_action": next_action,
        "appointment_requested": appointment_requested,
        "follow_up_required": interested and not appointment_requested,
    }


async def generate_summary(
    transcript: str,
    provider: str = "mock",
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """
    Generate a call summary. Uses mock in demo mode.

    In production, this would call OpenAI/Gemini/etc. via the configured provider.
    """
    if provider == "mock" or not api_key:
        return generate_mock_summary(transcript)

    # Placeholder for real LLM integration
    # Example with OpenAI:
    # from openai import OpenAI
    # client = OpenAI(api_key=api_key)
    # response = client.chat.completions.create(...)
    return generate_mock_summary(transcript)
