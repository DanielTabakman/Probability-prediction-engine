"""MSOS session resume v1 — product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def _read(*parts: str) -> str:
    return (MSOS_WEB.joinpath(*parts)).read_text(encoding="utf-8")


def test_valid_resume_restores_asset_window_region_and_expression() -> None:
    resume = _read("src", "lib", "regionBetResume.ts")
    card = _read("src", "components", "RegionBetResumeCard.tsx")
    shell = _read("src", "components", "RegionBetGuidedShell.tsx")
    assert "export function resolveRegionBetResume" in resume
    assert 'mode: "resume"' in resume
    assert "regionBet: input.stored" in resume
    assert "export function regionBetResumeRestoredFields" in resume
    assert "asset_id: regionBet.asset.asset_id" in resume
    assert "expiry_utc: regionBet.target.expiry_utc" in resume
    assert "window_start_utc: regionBet.target.window_start_utc" in resume
    assert "window_end_utc: regionBet.target.window_end_utc" in resume
    assert "selected_region: { ...regionBet.selected_region }" in resume
    assert "selected_expression_ref: regionBet.selected_expression_ref" in resume
    assert "regionBetResumeRestoredFields(resume.regionBet)" in card
    assert "restored.asset_id" in card
    assert "restored.expiry_utc" in card
    assert "restored.selected_region.price_min_usd" in card
    assert "restored.selected_expression_ref?.expression_id" in card
    assert "createRegionBetGuidedDraft(state.regionBet)" in shell
    assert "setStep(state.step)" in shell
    assert "fetchRegionBetResume" in shell


def test_invalid_navigation_falls_back_to_earliest_safe_incomplete_step() -> None:
    guided = _read("src", "lib", "regionBetGuidedShell.ts")
    resume = _read("src", "lib", "regionBetResume.ts")
    assert "export function isRegionBetGuidedShellStep" in guided
    assert "export function earliestSafeIncompleteRegionBetStep" in guided
    assert "export function resolveRegionBetGuidedShellResumeStep" in guided
    assert "if (isRegionBetGuidedShellStep(stored)) return stored" in guided
    assert "return earliestSafeIncompleteRegionBetStep(regionBet)" in guided
    assert 'if (!regionBetGuidedShellHasAsset(regionBet)) return "asset"' in guided
    assert 'if (!regionBetGuidedShellHasWindow(regionBet)) return "window"' in guided
    assert 'if (!regionBetGuidedShellHasRegion(regionBet)) return "region"' in guided
    assert 'return "compare"' in guided
    assert "resolveRegionBetGuidedShellResumeStep(storedStep, input.stored)" in resume


def test_malformed_stale_and_cross_owner_state_are_ignored() -> None:
    resume = _read("src", "lib", "regionBetResume.ts")
    store = _read("src", "lib", "msosWorkflowStore.ts")
    route = _read("src", "app", "api", "theses", "region-bet", "route.ts")
    assert 'return createCleanStartRegionBetResume("malformed")' in resume
    assert 'return createCleanStartRegionBetResume("cross_owner")' in resume
    assert 'return createCleanStartRegionBetResume("stale")' in resume
    assert 'return createCleanStartRegionBetResume("missing")' in resume
    assert "regionBetResumeOwnersMatch" in resume
    assert "isRegionBetResumeStale" in resume
    assert 'status === "closed"' in resume
    assert 'status === "archived"' in resume
    assert "regionBet: null" in resume
    assert "if (pointed && !regionBetOwnerMatches(pointed, ownerEmail))" in store
    assert 'return createCleanStartRegionBetResume("cross_owner")' in store
    assert "getMostRecentValidRegionBet" in store
    assert "resolveStoredRegionBetResume" in store
    assert "regionBetOwnerMatches(row, ownerEmail)" in store
    assert 'url.searchParams.get("resume") === "1"' in route
    assert "resolveStoredRegionBetResume(identity.email)" in route
    assert "regionBet: resume.regionBet" in route


def test_clean_start_path_is_available_without_silent_substitution() -> None:
    resume = _read("src", "lib", "regionBetResume.ts")
    card = _read("src", "components", "RegionBetResumeCard.tsx")
    shell = _read("src", "components", "RegionBetGuidedShell.tsx")
    assert "clean_start_available: true" in resume
    assert 'mode: "clean_start"' in resume
    assert "REGION_BET_RESUME_CLEAN_START_COPY" in resume
    assert "Start a clean paper draft instead of substituting another workspace" in resume
    assert "Start clean instead of substituting another owner's data" in card
    assert "Start clean" in card
    assert "onCleanStart" in card
    assert "createRegionBetGuidedDraft()" in shell
    assert "onCleanStart={startCleanDraft}" in shell
    assert "loadRegionBet()" not in resume
    assert "getCurrentRegionBet(" not in resume


def test_session_resume_is_paper_only_and_reuses_existing_store() -> None:
    resume = _read("src", "lib", "regionBetResume.ts")
    card = _read("src", "components", "RegionBetResumeCard.tsx")
    store = _read("src", "lib", "msosWorkflowStore.ts")
    client = _read("src", "lib", "regionBet.ts")
    route = _read("src", "app", "api", "theses", "region-bet", "route.ts")
    assert "paper_only: true" in resume
    assert "not financial advice" in resume.lower()
    assert "not a recommendation" in resume.lower()
    assert "not order execution" in resume.lower()
    assert "not financial advice" in card.lower()
    assert "Paper" in card
    assert "brokerage" not in resume.lower()
    assert "order ticket" not in resume.lower()
    assert "buy now" not in resume.lower()
    assert "financial advice" not in store.lower() or "not financial advice" in store.lower()
    assert 'fetch("/api/theses/region-bet?resume=1"' in resume
    assert 'credentials: "include"' in resume
    assert "upsertRegionBet" in store
    assert "msos.region.bet.extra" not in resume
    assert "msos.session.resume" not in store
    assert "localStorage.setItem" not in resume
    assert 'fetch("/api/theses/region-bet"' in client
    assert "getCurrentRegionBet" in route
    assert "upsertRegionBet" in route
    assert "requireProtectedIdentity" in route
