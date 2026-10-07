"""Utility helper functions."""

from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def calculate_temperature(score: int) -> str:
    if score >= 70:
        return "hot"
    elif score >= 40:
        return "warm"
    return "cold"
