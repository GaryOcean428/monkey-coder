"""Timezone-aware datetime utilities.

Centralizes UTC timestamp generation so we can migrate away from direct
usage of ``datetime.utcnow()`` (which returns a naive datetime) and ensure
all new code paths use aware datetimes. This also provides convenience
helpers for ISO8601 formatting with a canonical ``Z`` suffix.

Design decisions:
- ``utc_now()`` returns an aware datetime (UTC tzinfo) by default.
- ``naive=False`` can be supplied if legacy code still expects naive
  datetimes (temporary escape hatch during incremental migration).
- ``iso_now()`` returns a Z-suffixed ISO 8601 string (no microseconds
  trimming here—callers may `.removesuffix('Z')` if needed).

Future enhancements (roadmap):
- Inject clock for deterministic testing / time-freezing.
- Add monotonic interval helpers for latency accounting.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

__all__ = [
    "utc_now",
    "iso_now",
    "as_utc",
]

def utc_now(*, naive: bool = False) -> datetime:
    """Return the current UTC time as an aware datetime by default.

    Args:
        naive: When True, return a naive datetime (no tzinfo). Prefer leaving
               this False; provided only for transitional compatibility.
    """
    dt = datetime.now(timezone.utc)
    if naive:
        # Produce a copy without tzinfo for legacy comparisons.
        return dt.replace(tzinfo=None)
    return dt

def iso_now(*, naive: bool = False) -> str:
    """Return an ISO8601 string for the current UTC time with 'Z' suffix.

    Args:
        naive: If True, drop tzinfo before formatting (legacy support).
    """
    dt = utc_now(naive=naive)
    # If naive requested, isoformat without timezone then append Z for clarity.
    if naive and dt.tzinfo is None:
        return dt.isoformat() + "Z"
    return dt.isoformat().replace("+00:00", "Z")

def as_utc(dt: datetime) -> datetime:
    """Ensure a datetime is UTC-aware.

    If ``dt`` is naive it is assumed to already represent a UTC moment and
    will have UTC tzinfo attached (no conversion). If it has a timezone
    offset, it's converted to UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
