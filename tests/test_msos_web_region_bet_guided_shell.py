"""Region Bet guided shell v1 - product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_region_bet_guided_shell_declares_stepper_and_retained_snapshot() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "regionBetGuidedShell.ts").read_text(
        encoding="utf-8"
    )
    assert "REGION_BET_GUIDED_SHELL_STEPS" in lib
    assert '"asset"' in lib
    assert '"window"' in lib
    assert '"region"' in lib
    assert '"review"' in lib
    assert "buildRegionBetGuidedShellSnapshot" in lib
    assert "asset_id" in lib
    assert "expiry_utc" in lib
    assert "window_start_utc" in lib
    assert "window_end_utc" in lib
    assert "selected_region" in lib


def test_region_bet_guided_shell_uses_existing_contract_persistence() -> None:
    shell = (MSOS_WEB / "src" / "components" / "RegionBetGuidedShell.tsx").read_text(
        encoding="utf-8"
    )
    assert "fetchRegionBet" in shell
    assert "persistRegionBet" in shell
    assert "REGION_BET_PERSISTENCE_LABEL" in shell
    assert "createRegionBetGuidedDraft" in shell
    assert "applyRegionBetGuidedShellPatch" in shell
    assert "isRegionBetGuidedDraftPersistable" in shell


def test_region_bet_guided_shell_panel_preserves_context_across_steps() -> None:
    panel = (
        MSOS_WEB / "src" / "components" / "RegionBetGuidedShellPanel.tsx"
    ).read_text(encoding="utf-8")
    assert "RegionBetGuidedShellPanel" in panel
    assert "onDraftChange" in panel
    assert "snapshot" in panel
    assert "draft.asset.asset_id" in panel
    assert "draft.target.expiry_utc" in panel
    assert "draft.target.window_start_utc" in panel
    assert "draft.target.window_end_utc" in panel
    assert "draft.selected_region.price_min_usd" in panel
    assert "draft.selected_region.price_max_usd" in panel


def test_region_bet_guided_shell_fails_closed_before_persistence() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "regionBetGuidedShell.ts").read_text(
        encoding="utf-8"
    )
    shell = (MSOS_WEB / "src" / "components" / "RegionBetGuidedShell.tsx").read_text(
        encoding="utf-8"
    )
    assert "isRegionBetContract" in lib
    assert "price_min_usd >= region.price_max_usd" in lib
    assert "Date.parse(region.time_start_utc) > Date.parse(region.time_end_utc)" in lib
    assert "setSaveState(\"invalid\")" in shell
    assert "persistRegionBet(draft)" in shell


def test_region_bet_guided_shell_does_not_recreate_future_surfaces() -> None:
    touched = "\n".join(
        [
            (MSOS_WEB / "src" / "lib" / "regionBetGuidedShell.ts").read_text(
                encoding="utf-8"
            ),
            (
                MSOS_WEB / "src" / "components" / "RegionBetGuidedShell.tsx"
            ).read_text(encoding="utf-8"),
            (
                MSOS_WEB / "src" / "components" / "RegionBetGuidedShellPanel.tsx"
            ).read_text(encoding="utf-8"),
        ]
    )
    assert "OptionsExpressionFitRankingPanel" not in touched
    assert "OptionsHorizonComparison" not in touched
    assert "market compare" not in touched.lower()
    assert "brokerage" not in touched.lower()
    assert "order ticket" not in touched.lower()
