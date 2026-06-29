"""Gate: MSOS operator module map keeps required dashboard sections."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP_HTML = REPO / "docs" / "SOP" / "assets" / "msos_module_map.html"

REQUIRED_SECTIONS = (
    "Your attention — human to-do",
    "Waiting on time / data",
    "Recently shipped",
    "When you have bandwidth — backlog",
    "Module cards — gather, act, bottleneck",
)

OPERATOR_H2_ORDER = (
    "Your attention — human to-do",
    "Waiting on time / data",
    "Recently shipped",
    "When you have bandwidth — backlog",
)


def _html() -> str:
    return MAP_HTML.read_text(encoding="utf-8")


def test_module_map_file_exists() -> None:
    assert MAP_HTML.is_file()


def test_module_map_has_operator_sections() -> None:
    html = _html()
    for section in REQUIRED_SECTIONS:
        assert section in html, f"missing section: {section}"


def test_module_map_operator_section_order() -> None:
    html = _html()
    positions = [html.index(title) for title in OPERATOR_H2_ORDER]
    assert positions == sorted(positions), "operator panels must appear in attention → waiting → shipped → backlog order"


def test_module_map_last_updated_has_datetime() -> None:
    html = _html()
    assert 'id="map-last-updated"' in html
    match = re.search(r'data-last-updated="(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"', html)
    assert match is not None, "expected ISO datetime on data-last-updated"
    assert "<time datetime=" in html


def test_module_map_right_now_strip() -> None:
    html = _html()
    assert 'id="map-right-now"' in html
    assert "Trader Workflow Integration v1" in html
    assert "PPE_INTEGRATED_STATUS.md" in html


def test_module_map_quick_links() -> None:
    html = _html()
    assert 'id="map-quick-links"' in html
    assert "/options-horizon" in html
    assert "/strategy-lab" in html


def test_module_map_universe_expansion_row() -> None:
    html = _html()
    assert re.search(r"<td>7</td>\s*<td><strong>Universe expansion</strong>", html)


def test_module_map_gather_act_bottleneck_cards() -> None:
    html = _html()
    assert html.count('class="gather"') >= 7
    assert html.count('class="action"') >= 7
    assert html.count('class="bottleneck"') >= 7
    assert "7 · Universe expansion" in html


def test_module_map_integration_tiers_actionable_columns() -> None:
    html = _html()
    assert "What you gather" in html
    assert "What you can do" in html


def test_module_map_exposure_menu_live() -> None:
    html = _html()
    assert "Exposure menu v0 — /exposure route live" in html
    assert "6 · Exposure menu" in html and "T2 live" in html
    assert "approve READY → relay" not in html


def test_module_map_no_duplicate_operator_h2() -> None:
    html = _html()
    for title in OPERATOR_H2_ORDER:
        assert Counter(re.findall(r"<h2>([^<]+)</h2>", html))[title] == 1, f"duplicate h2: {title}"
