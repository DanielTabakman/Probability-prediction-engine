"""MSOS Options Horizon comparison surface checks."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_options_horizon_comparison_lib_is_educational_and_deterministic() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "optionsHorizonComparison.ts").read_text(encoding="utf-8")
    assert "TARGET_BUCKET_DAYS = [30, 60, 90, 180, 365]" in lib
    assert "Math.abs(a.daysOut - target)" in lib
    assert "HORIZON_COMPARISON_NO_ADVICE_COPY" in lib
    assert "not financial advice" in lib
    assert "not a recommendation" in lib
    assert "not order execution" in lib


def test_options_horizon_comparison_panel_renders_non_executable_table() -> None:
    panel = (MSOS_WEB / "src" / "components" / "OptionsHorizonComparisonPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert 'aria-label="Listed option horizon comparison"' in panel
    assert "<table" in panel
    assert "Target" in panel
    assert "Expiry" in panel
    assert "Forward" in panel
    assert "ATM IV" in panel
    assert "1 sigma" in panel
    assert "Rows are display-only" in panel
    assert "button" not in panel.lower()
    assert "trade" not in panel.lower()


def test_options_horizon_client_embeds_comparison_without_execution_copy() -> None:
    client = (MSOS_WEB / "src" / "components" / "OptionsHorizonClient.tsx").read_text(encoding="utf-8")
    assert "OptionsHorizonComparisonPanel" in client
    assert "buildOptionsHorizonComparisonFromChart(payload)" in client
    assert "comparison={comparison}" in client
