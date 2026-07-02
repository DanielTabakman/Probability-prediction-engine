"""MSOS storyboard visual parity v1 — witness slice (MSOS-VisParityV1-Witness-Slice008)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"
MSOS_WEB = REPO / "apps" / "msos-web"
APP = MSOS_WEB / "src" / "app"
COMPONENTS = MSOS_WEB / "src" / "components"
STORYBOARD = REPO / "docs" / "VISION" / "MSOS" / "storyboard-v0.6"

PLAN_REL = "docs/SOP/PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json"
PLAN = REPO / PLAN_REL
SPRINT = SOP / "SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md"
SELECTION = SOP / "POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md"
EVIDENCE = SOP / "MSOS_STORYBOARD_VISUAL_PARITY_V1_EVIDENCE_STATUS.md"
GLOBALS = APP / "globals.css"
STORYBOARD_CSS = STORYBOARD / "prototype" / "html" / "style.css"

STORYBOARD_SCREENS: tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("01_home", "/", "page.tsx", ("public-nav", "hero", "product-window", "features-row"), ()),
    (
        "02_command_center",
        "/command-center",
        "command-center/page.tsx",
        ("app-shell", "topline", "command-hero", "module-card-grid"),
        ("CommandCenterContent.tsx",),
    ),
    (
        "03_ppe_lab",
        "/strategy-lab",
        "strategy-lab/page.tsx",
        ("app-shell", "strategy-lab-work", "panel chart", "panel outcome"),
        ("StrategyLabWorkSection.tsx", "StrategyLabInteractivePanel.tsx"),
    ),
    (
        "04_confirmation",
        "/strategy-lab/confirm",
        "strategy-lab/confirm/page.tsx",
        ("confirm-wrap", "panel truth", "compare-row"),
        ("ThesisConfirmationPanel.tsx",),
    ),
    (
        "05_execution",
        "/strategy-lab/expression",
        "strategy-lab/expression/page.tsx",
        ("panel ticket", "execution-metrics", "exec-actions"),
        ("ExpressionPlanningPanel.tsx",),
    ),
    (
        "06_monitor",
        "/monitor",
        "monitor/page.tsx",
        ("monitor-lead", "monitor-panel", "monitor-watch-list"),
        ("MonitorContent.tsx", "MonitorWatchList.tsx"),
    ),
    (
        "07_history",
        "/history",
        "history/page.tsx",
        ("history-panel", "history-list"),
        ("HistoryContent.tsx",),
    ),
    (
        "08_updated_command",
        "/command-center",
        "command-center/page.tsx",
        ("buildCalibrationStrip", "command-hero"),
        ("CommandCenterContent.tsx",),
    ),
    (
        "09_conclusion",
        "/learn",
        "learn/page.tsx",
        ("learn-loop-strip", "conclusion-hero", "conclusion-layout"),
        ("ConclusionContent.tsx",),
    ),
)

REQUIRED_STORYBOARD_TOKENS = (
    "--bg",
    "--panel",
    "--line",
    "--text",
    "--muted",
    "--teal",
    "--cyan",
    "--amber",
    "--purple",
    "--red",
    "--shadow",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _css_vars(text: str) -> set[str]:
    return set(re.findall(r"(--[\w-]+)\s*:", text))


def test_charter_artifacts_exist() -> None:
    for path in (
        PLAN,
        SPRINT,
        SELECTION,
        EVIDENCE,
        STORYBOARD / "MANIFEST.md",
        STORYBOARD_CSS,
        STORYBOARD / "Market_Structure_OS_Website_Storyboard_v0.6.pdf",
    ):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_phase_plan_valid_and_witness_slice_present() -> None:
    plan = json.loads(_read(PLAN))
    assert not validate_phase_plan(plan)
    slice_ids = [s["sliceId"] for s in plan["slices"]]
    assert "MSOS-VisParityV1-Witness-Slice008" in slice_ids
    witness = next(s for s in plan["slices"] if s["sliceId"] == "MSOS-VisParityV1-Witness-Slice008")
    touch = witness.get("touchSet") or []
    assert any("MSOS_STORYBOARD_VISUAL_PARITY_V1_EVIDENCE_STATUS" in t for t in touch)
    assert any(t.startswith("tests/test_msos_web_") for t in touch)


def test_storyboard_css_tokens_traced_in_globals() -> None:
    storyboard_vars = _css_vars(_read(STORYBOARD_CSS))
    globals_vars = _css_vars(_read(GLOBALS))
    missing = [token for token in REQUIRED_STORYBOARD_TOKENS if token not in globals_vars]
    assert not missing, f"globals.css missing storyboard tokens: {missing}"
    assert REQUIRED_STORYBOARD_TOKENS[0] in storyboard_vars


def test_storyboard_screen_routes_and_layout_markers() -> None:
    feed_lib = _read(MSOS_WEB / "src" / "lib" / "monitorHistoryFeed.ts")
    for screen_id, route, page_rel, markers, component_names in STORYBOARD_SCREENS:
        page_path = APP / page_rel
        assert page_path.is_file(), f"{screen_id}: missing route page {page_rel}"

        page_text = _read(page_path)
        component_text = "".join(_read(COMPONENTS / name) for name in component_names)
        combined = page_text + component_text + _read(GLOBALS)
        if screen_id == "08_updated_command":
            combined += feed_lib

        for marker in markers:
            assert marker in combined, f"{screen_id} ({route}): missing layout marker {marker!r}"


def test_homepage_uses_storyboard_shell_classes() -> None:
    home = _read(APP / "page.tsx")
    assert 'className="page"' in home
    assert "PublicNav" in home
    assert "HeroSection" in home
    assert "ProductWindow" in home
    assert "FeaturesRow" in home


def test_app_shell_used_on_journey_routes() -> None:
    app_routes = (
        APP / "command-center" / "page.tsx",
        APP / "strategy-lab" / "page.tsx",
        APP / "monitor" / "page.tsx",
        APP / "history" / "page.tsx",
        APP / "learn" / "page.tsx",
    )
    for route in app_routes:
        text = _read(route)
        assert "AppShell" in text, f"missing AppShell on {route.relative_to(REPO)}"


def test_evidence_visual_witness_checkboxes_checked() -> None:
    text = _read(EVIDENCE)
    unchecked = re.findall(r"\|\s*`0[1-9]_[^`]+`\s*\|[^|]+\|\s*\[\s*\]\s*\|", text)
    assert not unchecked, f"unchecked visual witnesses: {unchecked}"
    checked = re.findall(r"\|\s*`0[1-9]_[^`]+`\s*\|[^|]+\|\s*\[x\]\s*\|", text, flags=re.IGNORECASE)
    assert len(checked) == 9, f"expected 9 checked witnesses, found {len(checked)}"


def test_evidence_witness_slice_complete() -> None:
    text = _read(EVIDENCE)
    assert "MSOS-VisParityV1-Witness-Slice008" in text
    assert re.search(
        r"MSOS-VisParityV1-Witness-Slice008\s*\|\s*(COMPLETE|WITNESSED|CLOSED)",
        text,
        flags=re.IGNORECASE,
    ), "witness slice must be marked complete in evidence doc"
