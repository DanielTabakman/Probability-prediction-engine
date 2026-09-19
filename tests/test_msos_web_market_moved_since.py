"""MSOS market moved since v1 — product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def _read(*parts: str) -> str:
    return (MSOS_WEB.joinpath(*parts)).read_text(encoding="utf-8")


def test_change_mapping_uses_deterministic_calculations_only() -> None:
    lib = _read("src", "lib", "marketMovedSince.ts")
    contract = _read("src", "lib", "regionBet.ts")
    assert "buildMarketMovedSinceSummary" in lib
    assert "mapMarketMovedSinceChange" in lib
    assert "resolveRegionBetLastSeenSnapshot" in lib
    assert "now_usd - input.last_seen_usd" in lib
    assert "(deltaUsd / input.last_seen_usd) * 100" in lib
    assert 'MarketMovedSinceDirection = "up" | "down" | "unchanged" | "unavailable"' in lib
    assert 'source: "last_seen_snapshot"' in lib
    assert 'source: "frozen_entry_snapshot"' in lib
    assert 'source: "saved_entry"' in lib
    assert "last_seen_snapshot" in contract
    assert "buildRegionBetLastSeenSnapshot" in contract
    assert "regionBetHasLastSeenSnapshot" in contract
    assert "new Date()" not in lib
    assert "Math.random" not in lib
    assert "Date.now" not in lib


def test_both_observation_times_are_shown() -> None:
    lib = _read("src", "lib", "marketMovedSince.ts")
    card = _read("src", "components", "MarketMovedSinceCard.tsx")
    assert "last_seen_at_utc" in lib
    assert "last_seen_at_label" in lib
    assert "now_at_utc" in lib
    assert "now_at_label" in lib
    assert "observed_at_label" in lib
    assert "Last seen" in card
    assert "Now" in card
    assert "value.last_seen_at_label" in card
    assert "value.now_at_label" in card
    assert "Last-seen underlying" in card
    assert "Now underlying" in card
    assert "observation.observed_at_label" in card


def test_missing_incomparable_and_stale_inputs_are_labeled() -> None:
    lib = _read("src", "lib", "marketMovedSince.ts")
    card = _read("src", "components", "MarketMovedSinceCard.tsx")
    assert 'input_status: "missing"' in lib
    assert 'input_status: "incomparable"' in lib
    assert 'input_status: "stale"' in lib
    assert 'if (status === "missing") return "Missing input"' in lib
    assert 'if (status === "incomparable") return "Incomparable inputs"' in lib
    assert 'if (status === "stale") return "Stale input"' in lib
    assert "MARKET_MOVED_SINCE_STALE_AFTER_MS" in lib
    assert "nowMs < lastMs" in lib
    assert "nothing was fabricated" in lib
    assert "value.input_status_label" in card
    assert "qualifyMarketMovedSinceObservation" in lib
    assert 'quality: "unavailable"' in lib
    assert 'quality: "stale"' in lib


def test_same_normalized_summary_renders_on_monitor_and_history() -> None:
    feed = _read("src", "lib", "monitorHistoryFeed.ts")
    monitor = _read("src", "components", "MonitorContent.tsx")
    history = _read("src", "components", "HistoryContent.tsx")
    card = _read("src", "components", "MarketMovedSinceCard.tsx")
    assert "marketMovedSince?: MarketMovedSinceSummary | null" in feed
    assert "buildSharedMarketMovedSince" in feed
    assert "buildMarketMovedSinceSummary(regionBet" in feed
    assert "getCurrentRegionBet(email)" in feed
    assert "marketMovedSince," in feed
    assert "<MarketMovedSinceCard value={feed.marketMovedSince} />" in monitor
    assert "<MarketMovedSinceCard value={feed.marketMovedSince} />" in history
    assert 'data-testid="market-moved-since-card"' in card
    assert "Since you last looked" in card


def test_paper_only_copy_has_no_execution_prediction_or_advice_claims() -> None:
    lib = _read("src", "lib", "marketMovedSince.ts")
    card = _read("src", "components", "MarketMovedSinceCard.tsx")
    feed = _read("src", "lib", "monitorHistoryFeed.ts")
    monitor = _read("src", "components", "MonitorContent.tsx")
    history = _read("src", "components", "HistoryContent.tsx")
    assert "paper_only: true" in lib
    assert "not financial advice" in lib.lower()
    assert "not a recommendation" in lib.lower()
    assert "not order execution" in lib.lower()
    assert "do not claim causality or recommend an action" in lib
    assert "Paper observation only" in card
    assert "brokerage" not in lib.lower()
    assert "order ticket" not in lib.lower()
    assert "buy now" not in lib.lower()
    assert "predict" not in lib.lower()
    assert "will move" not in lib.lower()
    assert "brokerage" not in card.lower()
    assert "order ticket" not in card.lower()
    assert "predict" not in card.lower()
    assert "brokerage" not in monitor.lower()
    assert "brokerage" not in history.lower()
    assert "upsertRegionBet" not in feed
    assert "localStorage.setItem" not in lib
