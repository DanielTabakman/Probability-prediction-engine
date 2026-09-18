"""Region Bet payoff/save v1 product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def _read(relative: str) -> str:
    return (MSOS_WEB / relative).read_text(encoding="utf-8")


def test_region_bet_payoff_copy_is_deterministic_and_paper_only() -> None:
    lib = _read("src/lib/regionBetPayoff.ts")
    assert "buildRegionBetPayoffExplanation" in lib
    assert '"inside_region"' in lib
    assert '"below_region"' in lib
    assert '"above_region"' in lib
    assert "regionBet.selected_expression_ref" in lib
    assert "new Date(value)" in lib
    explanation_body = lib.split("export function buildRegionBetPayoffExplanation", 1)[
        1
    ].split("export function buildRegionBetFrozenEntrySnapshot", 1)[0]
    assert "new Date()" not in explanation_body
    assert "Math.random" not in explanation_body
    assert "not financial advice" in lib
    assert "not a recommendation" in lib
    assert "not order execution" in lib
    assert "broker" not in lib.lower()
    assert "order ticket" not in lib.lower()


def test_confirmation_freezes_required_entry_snapshot_fields() -> None:
    contract = _read("src/lib/regionBet.ts")
    payoff = _read("src/lib/regionBetPayoff.ts")
    for field in (
        "confirmed_at_utc",
        "entry",
        "spot_usd",
        "timestamp_utc",
        "market_snapshot",
        "as_of_utc",
        "risk_constraints",
        "selected_region",
        "selected_expression_ref",
    ):
        assert field in contract
        assert field in payoff
    assert "buildRegionBetFrozenEntrySnapshot" in payoff
    assert "status: \"active\"" in payoff
    assert "confirmed: boolean" in payoff


def test_guided_shell_requires_explicit_payoff_confirmation_for_activation() -> None:
    shell = _read("src/components/RegionBetGuidedShell.tsx")
    panel = _read("src/components/RegionBetPayoffSavePanel.tsx")
    guided_panel = _read("src/components/RegionBetGuidedShellPanel.tsx")
    assert "confirmRegionBetPayoff(draft, { confirmed: true })" in shell
    assert "persistRegionBet(confirmed, { confirmPayoff: true })" in shell
    assert "RegionBetPayoffSavePanel" in guided_panel
    assert "I confirm this paper payoff explanation" in panel
    assert "disabled={!canConfirm || status === \"saving\"}" in panel
    assert "Confirm and save" in panel
    assert "Save draft" in shell


def test_api_and_store_reject_unconfirmed_or_mutated_active_region_bets() -> None:
    store = _read("src/lib/msosWorkflowStore.ts")
    route = _read("src/app/api/theses/region-bet/route.ts")
    client = _read("src/lib/regionBet.ts")
    assert "confirmPayoff?: boolean" in client
    assert "body: JSON.stringify({ regionBet, confirmPayoff: options.confirmPayoff === true })" in client
    assert "confirmPayoff: body?.confirmPayoff === true" in route
    assert "explicit payoff confirmation required" in store
    assert "active region bet requires a frozen entry snapshot" in store
    assert "active region bet has malformed payoff confirmation input" in store
    assert "frozen entry snapshot is immutable" in store
    assert "regionBetFrozenSnapshotKey(existing.frozen_entry_snapshot)" in store


def test_restore_contract_accepts_frozen_snapshot_and_preserves_owner_scope() -> None:
    contract = _read("src/lib/regionBet.ts")
    store = _read("src/lib/msosWorkflowStore.ts")
    assert "isRegionBetFrozenEntrySnapshot(row.frozen_entry_snapshot)" in contract
    assert "ownerEmail: owner" in store
    assert "regionBetOwnerMatches(row, ownerEmail)" in store
    assert "regionBetId: next.id" in store
