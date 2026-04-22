"""
Local UI smoke harness for `src/viz/app.py` (implied lab).

Narrow automated coverage (not a full scenario matrix): **A_width_target_payoff** is the
validated primary path. **C_directional_peak_disagreement** is a second gated scenario
with explicit manifest checks when run; do not treat C as “validated” unless that run’s
manifest booleans pass. Other scenario names in SCENARIOS remain ad-hoc / future work.

Runs:
1) Streamlit on a fixed local port
2) Waits for readiness
3) Drives the UI in a headless browser
4) Captures a screenshot per scenario executed in this run
5) Writes a per-run JSON manifest with verification booleans + screenshot paths
   (scenario A adds `slice003_witness` + `workflow_hardening_slice003_closeout` + optional
   `A_width_target_payoff_slice003_witness.png`)

Artifacts:
  artifacts/ui_smoke/<run_id>/
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
APP_ENTRY = ROOT / "src" / "viz" / "app.py"

ARTIFACTS_DIR = ROOT / "artifacts" / "ui_smoke"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = ARTIFACTS_DIR / RUN_ID


DEFAULT_PORT = 8502
PORT = int(os.environ.get("UI_SMOKE_PORT", str(DEFAULT_PORT)))
BASE_URL = f"http://127.0.0.1:{PORT}"
APP_URL = f"{BASE_URL}/"

# Sprint004-Slice003 (WH-Slice003): bounded witness of the width_vol candidate strip + session history UI.
SLICE003_CANDIDATE_HEADING = "Candidate to inspect (width-shaped, v0)"
SLICE003_HISTORY_SUMMARY = "History (this session)"
SLICE003_STRIP_WAIT_S = 55.0


SCENARIOS = [
    "A_width_target_payoff",
    "B_peak_aligned",
    "C_directional_peak_disagreement",
    "D_exact_strikes_mode",
]


@dataclass
class ScenarioResult:
    scenario: str
    page_loaded: bool = False
    disagreement_text_found: bool = False
    family_block_found: bool = False
    trade_ticket_found: bool = False
    verification_found: bool = False
    directional_category_verified: bool = False
    screenshot_path: str = ""
    notes: str = ""
    # WH-Slice003 witness (scenario A only; see slice003_witness in manifest).
    slice003_classification: str = "NOT_APPLICABLE"
    slice003_candidate_strip_found: bool = False
    slice003_history_expander_found: bool = False
    slice003_clear_history_control_found: bool = False
    slice003_witness_screenshot_path: str = ""
    slice003_region_witness_saved: bool = False
    slice003_used_union_clip: bool = False
    slice003_region_witness_clip_px: dict[str, float] | None = None
    slice003_region_dom_anchor: str = ""
    slice003_witness_notes: str = ""


def _port_is_listening(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_streamlit() -> subprocess.Popen[str]:
    """
    Start streamlit in the background and return the process handle.
    """
    if not APP_ENTRY.exists():
        raise FileNotFoundError(f"Missing Streamlit entry: {APP_ENTRY}")

    # Streamlit binds to port early, so treat already-listening as "do not stomp".
    if _port_is_listening(PORT):
        raise RuntimeError(
            f"Port {PORT} already in use. Stop other servers or set UI_SMOKE_PORT."
        )

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_ENTRY),
        "--server.address",
        "127.0.0.1",
        "--server.port",
        str(PORT),
        "--server.headless",
        "true",
    ]

    # Keep output in a file for debugging; don't spam stdout.
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    log_path = RUN_DIR / "streamlit.log"
    log_f = log_path.open("w", encoding="utf-8", errors="replace")

    env = dict(os.environ)
    # Reduce Streamlit telemetry noise.
    env.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc


def wait_for_streamlit_ready(timeout_s: float = 300.0) -> None:
    """
    Wait until:
    1) TCP port is accepting connections
    2) The main page HTTP endpoint returns 200 at least once

    The implied lab performs network calls on first load, so the initial
    response can be slow; this readiness check avoids brittle HTML matching.
    """
    deadline = time.time() + timeout_s
    last_err: str = ""

    # Step 1: wait for TCP accept.
    while time.time() < deadline:
        if _port_is_listening(PORT):
            break
        time.sleep(0.5)

    # Step 2: wait for initial HTML.
    while time.time() < deadline:
        try:
            r = requests.get(APP_URL, timeout=5)
            if r.status_code == 200 and len(r.text) > 1000:
                return
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
        time.sleep(1.0)

    raise TimeoutError(
        f"Streamlit not ready within {timeout_s}s. Last error: {last_err}"
    )


def _ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium\n\n"
            f"Original error: {e}"
        ) from e


def _parse_sigma_mkt_at_horizon_from_caption(page) -> float | None:
    """
    Parse belief summary line:
      σ_ln: user <...> · ATM-implied @ horizon <num> · width band vs market: ...
    """
    try:
        loc = page.locator("text=/ATM-implied @ horizon [0-9.]+/").first
        if loc.count() == 0:
            return None
        txt = loc.inner_text()
        m = re.search(r"ATM-implied @ horizon\s+([0-9.]+)", txt)
        if not m:
            return None
        return float(m.group(1))
    except Exception:
        return None


def _parse_width_band_from_belief_summary(page) -> str | None:
    """
    Parse belief summary line:
      σ_ln: user <...> · ATM-implied @ horizon <num> · width band vs market: <band>
    Returns: "narrower" | "similar" | "wider" (or None if not found)
    """
    try:
        loc = page.locator("text=/width band vs market:/").first
        if loc.count() == 0:
            return None
        txt = loc.inner_text()
        m = re.search(r"width band vs market:\s*(narrower|similar|wider)", txt, re.IGNORECASE)
        if not m:
            return None
        return str(m.group(1)).lower()
    except Exception:
        return None


def _parse_disagreement_type_line(page) -> str | None:
    """
    Extract the current disagreement type label from the belief hints markdown.
    Example: "Disagreement type: Directional (bullish)"
    """
    try:
        body = page.locator("body").inner_text()
        m = re.search(r"Disagreement type:\s*([^\n\r]+)", body, re.IGNORECASE)
        if not m:
            return None
        return m.group(0).strip()
    except Exception:
        return None


def _parse_forward_usd_from_caption(page) -> float | None:
    """
    Parse right-panel caption text:
      Forward $<num> · ATM IV <...>% · T = <...> yr
    """
    try:
        # Regex is applied inside Playwright selector.
        loc = page.locator(r"text=/Forward \\$[0-9,]+/").first
        if loc.count() == 0:
            return None
        txt = loc.inner_text()
        m = re.search(r"Forward \\$([0-9,]+)", txt)
        if not m:
            return None
        return float(m.group(1).replace(",", ""))
    except Exception:
        return None


def _wait_for_visible_text(page, text: str, timeout_s: float = 45.0) -> None:
    page.wait_for_selector(f"text={text}", timeout=int(timeout_s * 1000), state="visible")


def _set_belief_enabled(page, enabled: bool) -> None:
    """
    Toggle belief overlay checkbox.

    Streamlit's checkbox labeling isn't always exposed to Playwright's
    get_by_label(), so we use a text-based approach and validate via the
    presence of the belief disagreement text block.
    """

    def _disagreement_visible() -> bool:
        try:
            loc = page.locator("text=Disagreement type:").first
            return loc.count() > 0 and loc.is_visible()
        except Exception:
            return False

    currently_enabled = _disagreement_visible()
    if enabled and currently_enabled:
        return
    if (not enabled) and (not currently_enabled):
        return

    # Click the checkbox label text; this should toggle the underlying input.
    cb_label = page.locator("text=Show my belief curve").first
    if cb_label.count() == 0:
        raise RuntimeError("Could not find belief curve checkbox label text.")
    cb_label.click()

    # Wait briefly for the belief block to update.
    page.wait_for_timeout(1200)


def _set_number_input_by_label_regex(page, label_regex: str, value: float) -> None:
    """
    Set a Streamlit number input by its visible label.
    """
    import re as _re

    inp = page.get_by_label(_re.compile(label_regex, _re.IGNORECASE)).first
    if inp.count() == 0:
        # Fallback: look for a label substring and then the first adjacent number input.
        fallback_sub = "Belief peak" if "Belief peak" in label_regex else "Belief peak"
        inp = page.locator(
            f"xpath=//*[contains(normalize-space(.), '{fallback_sub}')]/following::input[@type='number'][1]"
        ).first
        if inp.count() == 0:
            raise RuntimeError(
                f"Could not find numeric input (fallback) for label regex: {label_regex}"
            )

    # Streamlit may be locked by focus; fill + enter is the most reliable.
    inp.click()
    inp.fill(str(int(round(value))))
    inp.press("Enter")


def _set_slider_by_label_regex(page, label_regex: str, value: float) -> None:
    """
    Set Streamlit slider (range input) by label.
    """
    import re as _re

    slider = page.get_by_label(_re.compile(label_regex, _re.IGNORECASE)).first
    if slider.count() == 0:
        fallback_sub = "Uncertainty"
        slider = page.locator(
            f"xpath=//*[contains(normalize-space(.), '{fallback_sub}')]/following::input[@type='range'][1]"
        ).first
        if slider.count() == 0:
            raise RuntimeError(f"Could not find slider (fallback) for label regex: {label_regex}")

    # Slider is typically <input type="range">; set value and dispatch input/change.
    v = float(value)
    slider.evaluate(
        """
        (el, v) => {
          el.value = String(v);
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """,
        v,
    )


def _set_belief_uncertainty_aria_slider(page, value: float) -> None:
    """
    Streamlit renders belief width as a Base Web `div[role=slider]`, not `<input type=range>`.
    Scope to the 'My belief vs market' expander so sidebar sliders are not touched.
    """
    details = page.locator("details").filter(
        has=page.locator("summary", has_text="My belief vs market")
    ).first
    if details.count() == 0:
        raise RuntimeError("Belief expander not found")

    # Ensure the uncertainty mode is σ_ln so the harness is setting the right control.
    try:
        details.locator("text=σ_ln (advanced)").first.click(timeout=2000)
        page.wait_for_timeout(250)
    except Exception:
        pass
    # First try the Base Web slider role (older Streamlit).
    slider = details.get_by_role("slider").first
    if slider.count() > 0:
        # Slider step in the app may be finer than 0.01; keep extra precision.
        target = float(max(0.02, min(0.8, round(value, 3))))
        slider.click()
        for _ in range(400):
            cur = float(slider.get_attribute("aria-valuenow") or "0.02")
            if abs(cur - target) < 0.0025:
                break
            if cur < target - 0.002:
                page.keyboard.press("ArrowRight")
            else:
                page.keyboard.press("ArrowLeft")
            page.wait_for_timeout(25)
        page.wait_for_timeout(400)
        return

    # Newer Streamlit: <input type="range"> inside expander.
    rng = details.locator("input[type='range']").first
    if rng.count() > 0:
        v = float(max(0.02, min(0.8, value)))
        rng.evaluate(
            """
            (el, v) => {
              el.value = String(v);
              el.dispatchEvent(new Event('input', { bubbles: true }));
              el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """,
            v,
        )
        page.wait_for_timeout(500)
        return

    raise RuntimeError("Belief uncertainty slider not found")


def _set_mode(page, mode_text: str) -> None:
    # Sprint 001 — Slice 008 (Phase 2): mode radio lives inside a collapsed expander.
    _expand_expander(page, "Mode & solver (Exact strikes vs Target payoff)")
    # Streamlit radio is usually rendered as clickable elements by label text.
    loc = page.locator(f"text={mode_text}").first
    if loc.count() == 0:
        # Fallback to partial matching.
        loc = page.locator("text=Mode").locator("xpath=following::*[contains(., '%s')][1]" % mode_text).first
    loc.click()


def _expand_expander(page, expander_title: str) -> None:
    """
    Click a <details><summary>... expander if not already open.
    """
    try:
        page.wait_for_selector(f"text={expander_title}", timeout=90000, state="attached")
    except Exception:
        pass

    summary = page.locator("details summary").filter(
        has_text=re.compile(re.escape(expander_title), re.I)
    ).first
    if summary.count() == 0:
        summary = page.locator("summary").filter(
            has_text=re.compile(re.escape(expander_title), re.I)
        ).first

    if summary.count() > 0:
        details = summary.locator("xpath=ancestor::details[1]").first
        if details.get_attribute("open") is None:
            try:
                summary.scroll_into_view_if_needed()
            except Exception:
                pass
            summary.click()
            page.wait_for_timeout(800)
        return

    header = page.get_by_role("button", name=re.compile(re.escape(expander_title), re.I)).first
    if header.count() > 0:
        try:
            header.scroll_into_view_if_needed()
        except Exception:
            pass
        header.click(force=True)
        page.wait_for_timeout(800)
        return

    raise RuntimeError(f"Could not find expander header: {expander_title}")


def _collect_observations(page, result: ScenarioResult) -> None:
    def _text_present(substr: str) -> bool:
        try:
            loc = page.locator(f"text={substr}").first
            return loc.count() > 0
        except Exception:
            return False

    # Disagreement/family text comes from belief overlay markdown.
    # Use presence (count) rather than visibility so offscreen column content
    # doesn't get misclassified as "not found".
    result.disagreement_text_found = _text_present("Disagreement type:")
    result.family_block_found = _text_present("Strategy families that fit this disagreement")
    result.trade_ticket_found = _text_present("Trade ticket (copy/paste)")


def _collect_verification_observation(page, result: ScenarioResult) -> None:
    try:
        loc = page.locator("text=disagreement classification").first
        # Visible check distinguishes expanded-vs-collapsed expander content
        # (and avoids matching hidden/collapsed DOM).
        # For the harness we care that the expander content is rendered,
        # not that it's within the current viewport.
        result.verification_found = loc.count() > 0
    except Exception:
        result.verification_found = False


def _collect_directional_category_verification(page, result: ScenarioResult) -> None:
    """Scenario C: belief-vs-market category must be directional (peak off, width similar)."""
    if result.scenario != "C_directional_peak_disagreement":
        return
    try:
        line = _parse_disagreement_type_line(page) or ""
        result.directional_category_verified = bool(re.search(r"Directional", line, re.IGNORECASE))
        if not result.directional_category_verified:
            wb = _parse_width_band_from_belief_summary(page)
            if wb:
                result.notes = (result.notes + " | " if result.notes else "") + f"width_band={wb}"
            if line:
                result.notes = (result.notes + " | " if result.notes else "") + f"disagreement_line={line}"
    except Exception:
        result.directional_category_verified = False


def _slice003_strip_root_locator(page, heading: Any) -> tuple[Any, str]:
    """
    Prefer Streamlit bordered vertical wrapper that contains the strip + hypothesis caption
    (colocated in `right_width_candidate_slot` in app.py).
    """
    try:
        bordered = page.locator('[data-testid="stVerticalBlockBorderWrapper"]').filter(
            has_text=re.compile(r"Candidate to inspect", re.I)
        )
        if bordered.count() > 0:
            return bordered.first, "stVerticalBlockBorderWrapper"
    except Exception:
        pass
    return heading, "candidate_heading"


def _slice003_union_clip(page, *locs: Any) -> dict[str, float] | None:
    """Union locator bounding boxes in viewport CSS pixels for a single bounded screenshot."""
    boxes: list[dict[str, float]] = []
    vp = page.viewport_size or {"width": 1400, "height": 950}
    vw, vh = float(vp["width"]), float(vp["height"])
    for loc in locs:
        if loc is None:
            continue
        try:
            if getattr(loc, "count", lambda: 0)() == 0:
                continue
            handle = loc.element_handle()
            if handle is None:
                continue
            bb = handle.bounding_box()
            if bb and float(bb["width"]) > 1 and float(bb["height"]) > 1:
                boxes.append(bb)
        except Exception:
            continue
    if not boxes:
        return None
    x0 = min(float(b["x"]) for b in boxes)
    y0 = min(float(b["y"]) for b in boxes)
    x1 = max(float(b["x"]) + float(b["width"]) for b in boxes)
    y1 = max(float(b["y"]) + float(b["height"]) for b in boxes)
    pad = 8.0
    x0, y0 = max(0.0, x0 - pad), max(0.0, y0 - pad)
    x1, y1 = min(vw, x1 + pad), min(vh, y1 + pad)
    w, h = max(1.0, x1 - x0), max(1.0, y1 - y0)
    return {"x": x0, "y": y0, "width": w, "height": h}


def _collect_slice003_witness(page, result: ScenarioResult) -> None:
    """
    Narrow, selector-based witness for Sprint004-Slice003 UI (candidate strip + session history).

    One bounded viewport clip screenshot covering strip root + History expander + Clear history
    once all three are reachable (scroll-to-region, no full-page framework).
    Classifications are machine-stable for manifest closeout.
    """
    if result.scenario != "A_width_target_payoff":
        result.slice003_classification = "NOT_APPLICABLE"
        return

    if not result.page_loaded:
        result.slice003_classification = "DEGRADED_PAGE_NOT_LOADED"
        result.slice003_witness_notes = "App shell did not reach a loaded state."
        return

    if result.notes:
        result.slice003_classification = "DEGRADED_SCENARIO_INCOMPLETE"
        result.slice003_witness_notes = result.notes[:800]
        return

    if not result.verification_found:
        result.slice003_classification = "DEGRADED_VERIFICATION_UI_NOT_REACHED"
        result.slice003_witness_notes = (
            "Primary scenario controls ran, but disagreement classification UI was not observed."
        )
        return

    heading = page.get_by_text(
        re.compile(r"Candidate\s+to\s+inspect\s*\(width-shaped,\s*v0\)", re.I)
    ).first
    try:
        heading.wait_for(state="attached", timeout=int(SLICE003_STRIP_WAIT_S * 1000))
    except Exception as e:  # noqa: BLE001
        result.slice003_classification = "DEGRADED_STRIP_NOT_SHOWN"
        result.slice003_witness_notes = (
            "Live verification did not surface the width_vol candidate strip within the bounded wait "
            f"({SLICE003_STRIP_WAIT_S:.0f}s). Same gate as app `disagreement_category_id == width_vol`. "
            f"Last error: {type(e).__name__}: {e}"
        )
        return

    result.slice003_candidate_strip_found = True
    strip_root, anchor = _slice003_strip_root_locator(page, heading)
    result.slice003_region_dom_anchor = anchor
    try:
        strip_root.scroll_into_view_if_needed()
    except Exception:
        pass
    try:
        heading.scroll_into_view_if_needed()
    except Exception:
        pass
    page.wait_for_timeout(350)

    hist_summary = page.locator("summary").filter(
        has_text=re.compile(re.escape(SLICE003_HISTORY_SUMMARY), re.I)
    ).first
    if hist_summary.count() == 0:
        result.slice003_classification = "PARTIAL_DOM"
        result.slice003_witness_notes = (
            "Candidate strip visible but History (this session) expander not found "
            "(session history renders only after at least one width_vol appearance event)."
        )
        return

    result.slice003_history_expander_found = True
    details_el = hist_summary.locator("xpath=ancestor::details[1]").first
    try:
        if details_el.count() > 0 and details_el.get_attribute("open") is None:
            hist_summary.click()
            page.wait_for_timeout(450)
    except Exception:
        pass

    clear_btn = page.get_by_role("button", name=re.compile(r"Clear\s+history", re.I)).first
    result.slice003_clear_history_control_found = False
    try:
        clear_btn.wait_for(state="visible", timeout=8000)
        result.slice003_clear_history_control_found = True
    except Exception:
        try:
            fallback = page.locator("button", has_text=re.compile(r"Clear\s+history", re.I)).first
            if fallback.count() > 0 and fallback.is_visible():
                result.slice003_clear_history_control_found = True
                clear_btn = fallback
        except Exception:
            result.slice003_clear_history_control_found = False

    if not result.slice003_clear_history_control_found:
        result.slice003_classification = "PARTIAL_DOM"
        result.slice003_witness_notes = (
            "Clear history control not visible after opening History expander."
        )
        return

    for loc in (strip_root, details_el, clear_btn):
        try:
            if loc is not None and getattr(loc, "count", lambda: 0)() > 0:
                loc.scroll_into_view_if_needed()
        except Exception:
            pass
    page.wait_for_timeout(300)

    witness_path = RUN_DIR / f"{result.scenario}_slice003_witness.png"
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    clip = _slice003_union_clip(page, strip_root, details_el, clear_btn)
    result.slice003_region_witness_clip_px = clip
    try:
        if clip:
            page.screenshot(path=str(witness_path), clip=clip)
            if witness_path.is_file() and witness_path.stat().st_size > 80:
                result.slice003_witness_screenshot_path = str(witness_path)
                result.slice003_region_witness_saved = True
                result.slice003_used_union_clip = True
        if not result.slice003_region_witness_saved:
            heading.screenshot(path=str(witness_path))
            if witness_path.is_file() and witness_path.stat().st_size > 80:
                result.slice003_witness_screenshot_path = str(witness_path)
                result.slice003_region_witness_saved = True
                result.slice003_used_union_clip = False
                result.slice003_witness_notes = (
                    "region_union_clip_unavailable_or_empty; saved heading-only fallback witness."
                )
    except Exception as ex:  # noqa: BLE001
        result.slice003_witness_notes = f"slice003_screenshot_failed: {type(ex).__name__}: {ex}"

    if not result.slice003_region_witness_saved:
        result.slice003_classification = "PARTIAL_DOM"
        if not result.slice003_witness_notes:
            result.slice003_witness_notes = (
                "Strip/history/clear were located in DOM but bounded screenshot did not persist."
            )
        return

    result.slice003_classification = "WITNESS_OK"


def take_screenshot(page, scenario: str) -> str:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    shot_path = RUN_DIR / f"{scenario}.png"
    page.screenshot(path=str(shot_path), full_page=False)
    return str(shot_path)


def run_one_scenario(page, scenario: str) -> ScenarioResult:
    r = ScenarioResult(scenario=scenario)

    # Page loaded check: title is static even when data is loading.
    try:
        _wait_for_visible_text(page, "Probability Prediction Engine", timeout_s=60.0)
        r.page_loaded = True
    except Exception:
        r.page_loaded = False
        if scenario == "A_width_target_payoff":
            r.slice003_classification = "DEGRADED_PAGE_NOT_LOADED"
            r.slice003_witness_notes = (
                "Shell/title visibility wait failed before implied lab content could be driven."
            )
        return r

    try:
        # The implied lab content is network-bound on first load; don't assume
        # the belief expander is present immediately.
        # Wait for the belief panel to mount; it appears only after expiry/marks load.
        page.wait_for_selector("text=My belief vs market", timeout=180000, state="attached")

        # Expand the belief expander so the checkbox + sliders become available.
        _expand_expander(page, "My belief vs market")

        # Ensure belief curve is enabled for disagreement/family checks.
        _set_belief_enabled(page, True)

        # Determine a good center anchor from the forward caption.
        forward = _parse_forward_usd_from_caption(page)
        # Fallback values to keep the UI drive logic alive even if parsing fails.
        if forward is None:
            forward = 70000.0

        # Set scenario-specific widgets.
        if scenario == "A_width_target_payoff":
            _set_mode(page, "Target payoff")
            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward)
            # Belief uncertainty now defaults to ±% mode; switch to σ mode so this scenario can set σ_ln.
            page.locator("text=σ_ln (advanced)").first.click()
            _set_slider_by_label_regex(page, r"Uncertainty", 0.70)
            _expand_expander(page, "Verification")
            # Scroll & wait for the classification block to be rendered.
            try:
                page.locator("text=disagreement classification").first.scroll_into_view_if_needed()
            except Exception:
                pass
            page.wait_for_selector(
                "text=disagreement classification",
                timeout=60000,
                state="attached",
            )

        elif scenario == "B_peak_aligned":
            _set_mode(page, "Exact strikes")
            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward)
            page.locator("text=σ_ln (advanced)").first.click()
            _set_slider_by_label_regex(page, r"Uncertainty", 0.20)

        elif scenario == "C_directional_peak_disagreement":
            _set_mode(page, "Exact strikes")
            # Match user σ_ln to ATM-implied σ first so width band is "similar", then
            # shift peak — yields directional (not mixed) disagreement vs market modal peak.
            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward)
            page.wait_for_timeout(1500)
            page.locator("text=σ_ln (advanced)").first.click()
            sig = _parse_sigma_mkt_at_horizon_from_caption(page)
            if sig is None:
                sig = 0.08
            sig = float(max(0.02, min(0.8, sig)))

            def _ensure_width_band_similar(target_sig: float) -> float:
                """
                Adjust the belief uncertainty slider until the UI reports width band = similar.
                This removes flakiness from rounding (e.g. σ_mkt very small) while preserving semantics.
                """
                # Try near the target with fine steps (slider supports ~0.01).
                candidates = []
                base = round(float(target_sig), 3)
                # Centered sweep: base, ±0.005, ±0.01, ...
                for d in [
                    0.0,
                    -0.005, 0.005,
                    -0.01, 0.01,
                    -0.015, 0.015,
                    -0.02, 0.02,
                    -0.025, 0.025,
                    -0.03, 0.03,
                ]:
                    v = float(max(0.02, min(0.8, base + d)))
                    if v not in candidates:
                        candidates.append(v)
                chosen = candidates[0]
                for v in candidates:
                    _set_belief_uncertainty_aria_slider(page, v)
                    page.wait_for_timeout(450)
                    wb = _parse_width_band_from_belief_summary(page)
                    chosen = v
                    if wb == "similar":
                        break
                return chosen

            chosen_sig = _ensure_width_band_similar(sig)
            page.wait_for_timeout(500)

            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward * 1.07)
            page.wait_for_timeout(900)
            # Peak change can rerun the script and reset the width slider; restore and re-ensure "similar".
            chosen_sig = _ensure_width_band_similar(chosen_sig)
            page.wait_for_timeout(600)
            _expand_expander(page, "Verification")
            try:
                page.locator("text=disagreement classification").first.scroll_into_view_if_needed()
            except Exception:
                pass
            page.wait_for_selector(
                "text=disagreement classification",
                timeout=60000,
                state="attached",
            )

        elif scenario == "D_exact_strikes_mode":
            _set_mode(page, "Exact strikes")
            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward)
            page.locator("text=σ_ln (advanced)").first.click()
            _set_slider_by_label_regex(page, r"Uncertainty", 0.20)
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        # Let Streamlit finish rerendering.
        page.wait_for_timeout(2000)

    except Exception as e:  # noqa: BLE001
        r.notes = f"{type(e).__name__}: {e}"

    # Screenshot + observation checks (even on failure).
    r.screenshot_path = take_screenshot(page, scenario)
    try:
        _collect_observations(page, r)
    except Exception:
        pass
    try:
        _collect_verification_observation(page, r)
    except Exception:
        pass
    try:
        _collect_directional_category_verification(page, r)
    except Exception:
        pass

    try:
        _collect_slice003_witness(page, r)
    except Exception as e:  # noqa: BLE001
        if r.scenario == "A_width_target_payoff":
            r.slice003_classification = "DEGRADED_SCENARIO_INCOMPLETE"
            r.slice003_witness_notes = f"slice003_witness_exception: {type(e).__name__}: {e}"

    return r


def main() -> int:
    _ensure_playwright()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    results: list[ScenarioResult] = []

    import argparse

    global PORT, BASE_URL, APP_URL

    parser = argparse.ArgumentParser(
        description=(
            "Implied lab local UI smoke harness (A validated; C gated when run — see manifest)."
        ),
    )
    parser.add_argument("--port", type=int, default=PORT, help="Local port to bind Streamlit")
    parser.add_argument(
        "--scenario",
        type=str,
        default="",
        help="If set, run only one scenario (must match one of SCENARIOS).",
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=300.0,
        help="Streamlit readiness timeout seconds.",
    )
    args = parser.parse_args()

    # Update globals in case caller overrides port.
    PORT = int(args.port)
    BASE_URL = f"http://127.0.0.1:{PORT}"
    APP_URL = f"{BASE_URL}/"

    proc: subprocess.Popen[str] | None = None
    try:
        proc = start_streamlit()
        wait_for_streamlit_ready(timeout_s=args.timeout_s)

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1400, "height": 950})
            page = context.new_page()

            # Navigate once; Streamlit updates in-place with widget changes.
            page.goto(APP_URL, wait_until="domcontentloaded")

            scenarios_to_run = SCENARIOS
            if args.scenario:
                if args.scenario not in SCENARIOS:
                    raise ValueError(f"Unknown scenario for --scenario: {args.scenario}")
                scenarios_to_run = [args.scenario]

            for scenario in scenarios_to_run:
                # For each scenario, reload the page to avoid cross-scenario widget state drift.
                page.goto(APP_URL, wait_until="domcontentloaded")
                page.wait_for_timeout(1500)
                results.append(run_one_scenario(page, scenario))

            browser.close()

        def _slice003_witness_row(r: ScenarioResult) -> dict[str, Any]:
            return {
                "classification": r.slice003_classification,
                "candidate_strip_heading_found": r.slice003_candidate_strip_found,
                "history_expander_found": r.slice003_history_expander_found,
                "clear_history_control_found": r.slice003_clear_history_control_found,
                "witness_screenshot_path": r.slice003_witness_screenshot_path,
                "region_witness_saved": r.slice003_region_witness_saved,
                "used_union_viewport_clip": r.slice003_used_union_clip,
                "region_dom_anchor": r.slice003_region_dom_anchor,
                "region_witness_clip_px": r.slice003_region_witness_clip_px,
                "notes": r.slice003_witness_notes,
            }

        def _slice003_closeout_block(rows: list[ScenarioResult]) -> dict[str, Any]:
            ra = next((x for x in rows if x.scenario == "A_width_target_payoff"), None)
            if ra is None:
                return {
                    "schema_version": 2,
                    "primary_scenario_ran": False,
                    "evidence_plane_complete": False,
                    "bounded_failure_bucket": "NOT_APPLICABLE",
                    "bounded_live_data_miss": False,
                    "bounded_app_or_data_unavailable": False,
                    "region_witness_artifact_ok": False,
                    "used_union_viewport_clip": False,
                    "workflow_hardening_slice003_signal": "NOT_APPLICABLE",
                    "detail": "A_width_target_payoff not in this run.",
                }
            cls = ra.slice003_classification
            bounded_live_miss = cls == "DEGRADED_STRIP_NOT_SHOWN"
            bounded_app_unreachable = cls in (
                "DEGRADED_PAGE_NOT_LOADED",
                "DEGRADED_SCENARIO_INCOMPLETE",
            )
            bounded_failure_bucket = {
                "WITNESS_OK": "OK",
                "DEGRADED_STRIP_NOT_SHOWN": "LIVE_DATA_NO_WIDTH_VOL_STRIP",
                "DEGRADED_PAGE_NOT_LOADED": "APP_OR_DATA_NOT_WITNESSABLE",
                "DEGRADED_SCENARIO_INCOMPLETE": "APP_OR_DATA_NOT_WITNESSABLE",
                "DEGRADED_VERIFICATION_UI_NOT_REACHED": "VERIFICATION_UI_NOT_REACHED",
                "PARTIAL_DOM": "SLICE003_DOM_INCOMPLETE",
                "NOT_APPLICABLE": "NOT_APPLICABLE",
            }.get(cls, "NEEDS_FIX_OR_RETRY")
            evidence_plane_complete = bounded_failure_bucket != "NEEDS_FIX_OR_RETRY"
            if cls == "WITNESS_OK":
                wf_signal = "WITNESS_OK"
            elif bounded_live_miss:
                wf_signal = "BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP"
            elif bounded_app_unreachable:
                wf_signal = "BOUNDED_APP_OR_DATA_UNAVAILABLE"
            elif cls == "DEGRADED_VERIFICATION_UI_NOT_REACHED":
                wf_signal = "BOUNDED_VERIFICATION_UI_NOT_REACHED"
            elif cls == "PARTIAL_DOM":
                wf_signal = "BOUNDED_SLICE003_DOM_INCOMPLETE"
            else:
                wf_signal = "NEEDS_FIX_OR_RETRY"
            return {
                "schema_version": 2,
                "primary_scenario_ran": True,
                "evidence_plane_complete": bool(evidence_plane_complete),
                "bounded_failure_bucket": bounded_failure_bucket,
                "bounded_live_data_miss": bool(bounded_live_miss),
                "bounded_app_or_data_unavailable": bool(bounded_app_unreachable),
                "classification": cls,
                "region_witness_artifact_ok": bool(ra.slice003_region_witness_saved),
                "used_union_viewport_clip": bool(ra.slice003_used_union_clip),
                "workflow_hardening_slice003_signal": wf_signal,
                "detail": ra.slice003_witness_notes or "",
            }

        wh_slice003_closeout = _slice003_closeout_block(results)

        # Write manifest.
        manifest = {
            "app_url": APP_URL,
            "port": PORT,
            "run_id": RUN_ID,
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "workflow_hardening_slice003_closeout": wh_slice003_closeout,
            "scenarios": [
                {
                    "scenario": r.scenario,
                    "page_loaded": r.page_loaded,
                    "disagreement_text_found": r.disagreement_text_found,
                    "family_block_found": r.family_block_found,
                    "trade_ticket_found": r.trade_ticket_found,
                    "verification_found": r.verification_found,
                    "directional_category_verified": r.directional_category_verified,
                    "screenshot_path": r.screenshot_path,
                    "notes": r.notes,
                    "slice003_witness": _slice003_witness_row(r),
                }
                for r in results
            ],
            "pass_criteria": {
                "harness_scope": (
                    "Narrow smoke harness (not a full scenario matrix): A_width_target_payoff "
                    "is validated. C_directional_peak_disagreement is a second gated scenario "
                    "(explicit checks below when included). B/D remain ad-hoc."
                ),
                "recommended_command": (
                    "python scripts/implied_lab_ui_smoke_harness.py --port <PORT> --scenario A_width_target_payoff"
                ),
                "success_requires": (
                    "For each scenario in this run: page_loaded, disagreement_text_found, "
                    "family_block_found, and trade_ticket_found must be true. "
                    "If A_width_target_payoff is included, verification_found must be true. "
                    "If C_directional_peak_disagreement is included, verification_found and "
                    "directional_category_verified must be true. "
                    "If neither A nor C is in the run, the verification gate fails."
                ),
                "future_work": (
                    "Expanding automated coverage beyond B/D ad-hoc scenarios and "
                    "tightening multi-scenario runs is optional follow-up."
                ),
                "note": (
                    "Official one-command wrapper (`scripts/run_implied_lab_ui_smoke.py`) runs "
                    "A_width_target_payoff only. For C, use --scenario C_directional_peak_disagreement; "
                    "a green run implies C’s manifest gates passed for that run."
                ),
                "workflow_hardening_slice003": (
                    "Scenario A collects `slice003_witness` (strip DOM, History expander, Clear history, "
                    "optional union viewport clip + `A_width_target_payoff_slice003_witness.png`) plus "
                    "`workflow_hardening_slice003_closeout` (schema v2: `bounded_failure_bucket`, "
                    "`region_witness_artifact_ok`, `used_union_viewport_clip`). "
                    "`evidence_plane_complete` is true when `bounded_failure_bucket` != NEEDS_FIX_OR_RETRY "
                    "(bounded terminals include WITNESS_OK, live strip miss, app/data unreachable, "
                    "verification-not-reached, partial DOM)."
                ),
            },
        }

        manifest_path = RUN_DIR / "ui_smoke_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Decide pass/fail for convenience (useful for local gatekeeping).
        def _all(cond: Any) -> bool:
            return all(bool(x) for x in cond)

        page_loaded_ok = _all(r.page_loaded for r in results)
        main_ok = _all(
            r.disagreement_text_found and r.family_block_found and r.trade_ticket_found
            for r in results
        )
        has_a = any(r.scenario == "A_width_target_payoff" for r in results)
        has_c = any(r.scenario == "C_directional_peak_disagreement" for r in results)
        verification_ok = True
        if has_a:
            ra = next(r for r in results if r.scenario == "A_width_target_payoff")
            verification_ok = verification_ok and bool(ra.verification_found)
        if has_c:
            rc = next(r for r in results if r.scenario == "C_directional_peak_disagreement")
            verification_ok = verification_ok and bool(
                rc.verification_found and rc.directional_category_verified
            )
        if not has_a and not has_c:
            verification_ok = False

        overall_pass = page_loaded_ok and main_ok and verification_ok

        summary_path = RUN_DIR / "ui_smoke_summary.txt"
        _a = next((x for x in results if x.scenario == "A_width_target_payoff"), None)
        _slice003_line = ""
        if _a is not None:
            _slice003_line = (
                f"slice003_classification={_a.slice003_classification}\n"
                f"slice003_evidence_plane_complete="
                f"{str(wh_slice003_closeout['evidence_plane_complete']).lower()}\n"
            )
        summary_path.write_text(
            (
                f"RUN_ID={RUN_ID}\n"
                f"PORT={PORT}\n"
                f"overall_pass={overall_pass}\n"
                f"page_loaded_ok={page_loaded_ok}\n"
                f"main_texts_ok={main_ok}\n"
                f"verification_ok={verification_ok}\n"
                f"{_slice003_line}"
            ),
            encoding="utf-8",
        )

        print(f"UI smoke manifest: {manifest_path}")
        print(f"Overall pass: {overall_pass}")
        return 0 if overall_pass else 1
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:
                try:
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                except Exception:
                    pass


if __name__ == "__main__":
    raise SystemExit(main())

