"""Region Bet monitor value v1 product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def _read(*parts: str) -> str:
    return (MSOS_WEB.joinpath(*parts)).read_text(encoding="utf-8")


def test_region_bet_monitor_maps_then_now_underlying_separately_from_expression() -> None:
    lib = _read("src", "lib", "regionBetMonitor.ts")
    contract = _read("src", "lib", "regionBet.ts")
    assert "buildRegionBetMonitorValue" in lib
    assert 'kind: "underlying" | "paper_expression"' in lib
    assert 'label: "entry" | "current"' in lib
    assert "underlyingEntry" in lib
    assert "underlyingCurrent" in lib
    assert "expressionEntry" in lib
    assert "expressionCurrent" in lib
    assert "frozen.entry.spot_usd" in lib
    assert "frozen.entry.timestamp_utc" in lib
    assert "later.spot_usd" in lib
    assert "later.expression_value_usd" in lib
    assert "later.entry_expression_value_usd" in lib
    assert "REGION_BET_OBSERVATION_QUALITIES" in contract
    assert 'value === "observed"' in contract
    assert 'value === "estimated"' in contract
    assert 'value === "stale"' in contract
    assert 'value === "unavailable"' in contract
    assert "regionBetHasFrozenEntrySnapshot" in contract
    assert "new Date()" not in lib
    assert "Math.random" not in lib


def test_region_bet_monitor_labels_quality_and_timestamps() -> None:
    lib = _read("src", "lib", "regionBetMonitor.ts")
    card = _read("src", "components", "RegionBetMonitorCard.tsx")
    assert "qualifyRegionBetObservation" in lib
    assert "observed_at_utc" in lib
    assert "observed_at_label" in lib
    assert "quality_label" in lib
    assert 'quality: "unavailable"' in lib
    assert 'quality: "stale"' in lib
    assert 'quality: "estimated"' in lib
    assert 'quality: "observed"' in lib
    assert "labelRegionBetObservationQuality" in lib
    assert 'if (quality === "observed") return "Observed"' in lib
    assert 'if (quality === "estimated") return "Estimated"' in lib
    assert 'if (quality === "stale") return "Stale"' in lib
    assert 'return "Unavailable"' in lib
    assert "observation.quality_label" in card
    assert "observation.observed_at_label" in card
    assert "Entry underlying" in card
    assert "Current underlying" in card
    assert "Entry paper-expression" in card
    assert "Current paper-expression" in card


def test_region_bet_monitor_stale_and_missing_expression_fail_closed() -> None:
    lib = _read("src", "lib", "regionBetMonitor.ts")
    feed = _read("src", "lib", "monitorHistoryFeed.ts")
    assert "REGION_BET_MONITOR_STALE_AFTER_MS" in lib
    assert "input.stale === true || isStaleByAge" in lib
    assert "if (valueUsd == null)" in lib
    assert 'quality: "unavailable"' in lib
    assert "nothing was fabricated" in lib
    assert "expression_value_usd: null" in feed
    assert "expression_observed_at_utc: null" in feed
    assert "getCurrentRegionBet(email)" in feed
    assert "buildRegionBetMonitorValue(regionBet" in feed
    assert "msos.region.bet.extra" not in feed
    assert "localStorage.setItem" not in lib


def test_region_bet_monitor_value_drivers_are_deterministic_and_paper_only() -> None:
    lib = _read("src", "lib", "regionBetMonitor.ts")
    card = _read("src", "components", "RegionBetMonitorCard.tsx")
    assert "explainRegionBetValueDrivers" in lib
    assert "value_drivers: explainRegionBetValueDrivers(value)" in lib
    assert "do not claim causality or recommend an action" in lib
    assert "separate observations" in lib
    assert "not financial advice" in lib.lower()
    assert "not a recommendation" in lib.lower()
    assert "not order execution" in lib.lower()
    assert "value.value_drivers.map" in card
    assert "value.limitation" in card
    assert "not financial advice" in card.lower() or "Paper only" in card
    assert "broker" not in lib.lower()
    assert "order ticket" not in lib.lower()
    assert "buy now" not in lib.lower()
    assert "new Date()" not in lib.split("export function explainRegionBetValueDrivers", 1)[1].split(
        "export function buildRegionBetLaterObservation", 1
    )[0]


def test_region_bet_monitor_reuses_existing_feed_and_owner_scoped_record() -> None:
    feed = _read("src", "lib", "monitorHistoryFeed.ts")
    content = _read("src", "components", "MonitorContent.tsx")
    route = _read("src", "app", "api", "monitor", "feed", "route.ts")
    card = _read("src", "components", "RegionBetMonitorCard.tsx")
    assert "regionBetMonitor?: RegionBetMonitorValue | null" in feed
    assert "getCurrentRegionBet" in feed
    assert "regionBetMonitor: feed.regionBetMonitor ?? null" in route
    assert "loadMonitorFeed(identity.email, displayCurrency)" in route
    assert "<RegionBetMonitorCard value={feed.regionBetMonitor} />" in content
    assert 'data-testid="region-bet-monitor-card"' in card
    assert "upsertRegionBet" not in feed
    assert "upsertRegionBet" not in route
    assert "/api/theses/region-bet" not in feed
    assert "brokerage" not in content.lower()
    assert "order ticket" not in content.lower()
    assert "brokerage" not in card.lower()
    assert "order ticket" not in card.lower()
