from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CanonicalEvent:
    """
    Canonical internal representation of an event we track probabilities for.

    This is intentionally small and additive; fields can grow as the engine
    matures without breaking existing stored observations.
    """

    id: str
    type: str
    asset: str | None
    threshold: float | None
    resolution_date: str | None  # ISO-8601 string (UTC preferred)
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ProbabilityObservation:
    canonical_event_id: str
    probability: float
    source: str
    as_of_utc: str  # ISO-8601 string (UTC preferred)
    raw_ref: str | None = None

