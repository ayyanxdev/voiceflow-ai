"""Date normalization utilities for appointment booking.

Retell AI frequently sends incorrect years (e.g. 2024 instead of 2026)
when the caller does NOT explicitly state a year.  This module corrects
that at the backend boundary so bad dates never reach the database.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional


def normalize_appointment_date(
    raw: str,
    *,
    reference: Optional[datetime] = None,
) -> datetime:
    """Parse an ISO-8601 string and return a timezone-aware datetime in
    the **future**.

    Algorithm
    1. Parse ``raw`` with ``datetime.fromisoformat``.
    2. If the result is timezone-naive, assume UTC.
    3. If the result is already in the future → return as-is.
    4. Otherwise, repeatedly add 1 year until it becomes future.
       This handles the common case where Retell sends the wrong year
       (e.g. 2024 instead of 2026).
    5. If adding a year overshoots (e.g. Feb 30 → Mar 2), Python rolls
       the date forward.  That's acceptable for appointments; the caller
       didn't give an explicit year, so the next valid occurrence is fine.

    Raises
    ------
    ValueError if the raw string is not valid ISO 8601.
    """
    try:
        dt = datetime.fromisoformat(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid ISO 8601 date: {raw!r}") from exc

    # Ensure timezone-aware (assume UTC for naive inputs from Retell)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = reference or datetime.now(timezone.utc)

    # Already in the future → nothing to do
    if dt > now:
        return dt

    # Date is in the past: bump year forward until future.
    # Cap at 10 iterations to avoid infinite loops on weird inputs.
    for _ in range(10):
        dt = dt.replace(year=dt.year + 1)
        if dt > now:
            return dt

    # Extremely unlikely fallback — just return the last bumped value.
    return dt
