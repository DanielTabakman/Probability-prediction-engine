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
    # True once the implied-lab belief UI anchor is present (same gate as prior harness).
    lab_mounted: bool = False
    # When lab_mounted is false: btc_spot_prerequisite, option_expiries_unavailable,
    # implied_distribution_exception, btc_spot_or_quote_feed_failure (log-inferred), timeout_lab_mount.
    lab_mount_blocker: str = ""
    disagreement_text_found: bool = False
    family_block_found: bool = False
    trade_ticket_found: bool = False
    verification_found: bool = False
    directional_category_verified: bool = False
    screenshot_path: str = ""
    notes: str = ""


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


def _classify_from_streamlit_log_tail(log_path: Path) -> str | None:
    """
    Infer data/feed failures that prevent the implied lab from mounting, using the Streamlit
    process log. Conservative: only returns a code when multiple corroborating signals appear.
    """
    try:
        raw = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    tail = raw[-48000:]
    low = tail.lower()
    if "deribit ticker failed" not in low and "deribit.com" not in low:
        return None
    if "failed download" not in low and "failed downloads" not in low:
        return None
    if "btc-usd" not in low:
        return None
    return "btc_spot_or_quote_feed_failure"


def _wait_for_implied_lab_mount(
    page,
    *,
    log_path: Path,
    timeout_s: float = 180.0,
    log_inference_after_s: float = 25.0,
) -> tuple[bool, str]:
    """
    Wait for the belief-panel anchor, or classify a pre-mount / data-gated failure early.

    Returns (mounted_ok, lab_mount_blocker). When mounted_ok is True, lab_mount_blocker is "".
    """
    deadline = time.time() + timeout_s
    start = time.time()
    poll_s = 1.25
    while time.time() < deadline:
        try:
            body = page.locator("body").inner_text(timeout=2500)
        except Exception:
            body = ""

        if "Need BTC spot price for implied distribution." in body:
            return False, "btc_spot_prerequisite"
        if "No Deribit option expiries" in body:
            return False, "option_expiries_unavailable"
        if "Implied distribution unavailable:" in body:
            return False, "implied_distribution_exception"

        try:
            loc = page.locator("text=My belief vs market").first
            if loc.count() > 0:
                return True, ""
        except Exception:
            pass

        # Implied lab still fetching; avoid treating parallel Yahoo/Deribit log lines as mount failure.
        if "Loading expiries and option marks" in body:
            time.sleep(poll_s)
            continue

        elapsed = time.time() - start
        if elapsed >= log_inference_after_s and log_path.is_file():
            inferred = _classify_from_streamlit_log_tail(log_path)
            if inferred:
                return False, inferred

        time.sleep(poll_s)

    return False, "timeout_lab_mount"


def _belief_curve_checkbox_checked(page) -> bool:
    """Read Streamlit checkbox state inside the belief expander (avoids false toggles when overlay copy is off-screen)."""
    try:
        details = page.locator("details").filter(
            has=page.locator("summary", has_text=re.compile(r"My belief vs market", re.I))
        ).first
        if details.count() == 0:
            return False
        inp = details.locator("input[type='checkbox']").first
        if inp.count() == 0:
            return False
        return bool(inp.is_checked())
    except Exception:
        return False


def _set_belief_enabled(page, enabled: bool) -> None:
    """
    Toggle belief overlay checkbox.

    Prefer checkbox DOM state over disagreement text visibility: first-touch UX
    may show disagreement lines in a different slot than older layouts, and
    off-screen markdown must not cause a spurious extra click (which would
    toggle belief off when it was already on).
    """
    if _belief_curve_checkbox_checked(page) == enabled:
        return

    cb_label = page.locator("text=Show my belief curve").first
    if cb_label.count() == 0:
        raise RuntimeError("Could not find belief curve checkbox label text.")
    cb_label.click()

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
        return r

    log_path = RUN_DIR / "streamlit.log"
    try:
        # The implied lab content is network-bound on first load; don't assume
        # the belief expander is present immediately.
        mounted, blocker = _wait_for_implied_lab_mount(page, log_path=log_path, timeout_s=180.0)
        r.lab_mounted = mounted
        r.lab_mount_blocker = blocker or ""
        if not mounted:
            r.notes = (
                f"implied_lab_not_mounted:{blocker}"
                + (f" | {r.notes}" if r.notes else "")
            ).strip()
            r.screenshot_path = take_screenshot(page, scenario)
            return r

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

        # Write manifest.
        manifest = {
            "app_url": APP_URL,
            "port": PORT,
            "run_id": RUN_ID,
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "scenarios": [
                {
                    "scenario": r.scenario,
                    "page_loaded": r.page_loaded,
                    "lab_mounted": r.lab_mounted,
                    "lab_mount_blocker": r.lab_mount_blocker,
                    "disagreement_text_found": r.disagreement_text_found,
                    "family_block_found": r.family_block_found,
                    "trade_ticket_found": r.trade_ticket_found,
                    "verification_found": r.verification_found,
                    "directional_category_verified": r.directional_category_verified,
                    "screenshot_path": r.screenshot_path,
                    "notes": r.notes,
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
        blockers = ",".join(sorted({r.lab_mount_blocker for r in results if r.lab_mount_blocker}))
        summary_path.write_text(
            (
                f"RUN_ID={RUN_ID}\n"
                f"PORT={PORT}\n"
                f"overall_pass={overall_pass}\n"
                f"page_loaded_ok={page_loaded_ok}\n"
                f"main_texts_ok={main_ok}\n"
                f"verification_ok={verification_ok}\n"
                f"lab_mount_blockers={blockers or '(none)'}\n"
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

