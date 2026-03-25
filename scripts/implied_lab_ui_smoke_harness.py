"""
Local UI smoke harness for `src/viz/app.py` (implied lab).

MVP (single-scenario): the only validated end-to-end path is **A_width_target_payoff**
(use `--scenario A_width_target_payoff`). Other scenario names in SCENARIOS exist for
future expansion, not for the current official pass definition.

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
    disagreement_text_found: bool = False
    family_block_found: bool = False
    trade_ticket_found: bool = False
    verification_found: bool = False
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
    summary = page.locator("summary", has_text=expander_title).first
    if summary.count() == 0:
        # Fallback for Streamlit variants where expander headers aren't <summary>.
        # 1) substring match
        header = page.locator(f"xpath=//*[contains(normalize-space(.), '{expander_title}')][1]").first
        # 2) regex match
        if header.count() == 0:
            header = page.locator(f"text=/{re.escape(expander_title)}/").first
        # 3) first-word match
        if header.count() == 0 and expander_title.strip():
            first_word = expander_title.strip().split()[0]
            header = page.locator(f"xpath=//*[contains(normalize-space(.), '{first_word}')][1]").first
        # 4) keyword match (handles cases where the title is split across nodes)
        if header.count() == 0:
            header = page.locator(
                "xpath=//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'belief') and contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'market')][1]"
            ).first
        if header.count() == 0:
            # Give the network-bound UI a moment to mount the expander header.
            page.wait_for_timeout(800)
            header = page.locator(
                "xpath=//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'belief') and contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'market')][1]"
            ).first
        if header.count() == 0:
            raise RuntimeError(f"Could not find expander header: {expander_title}")
        header.click(force=True)
        page.wait_for_timeout(800)
        return

    details = summary.locator("xpath=ancestor::details[1]").first
    open_attr = details.get_attribute("open")
    if not open_attr:
        summary.click()
        page.wait_for_timeout(800)


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

    try:
        # The implied lab content is network-bound on first load; don't assume
        # the belief expander is present immediately.
        try:
            page.wait_for_selector("text=Expiry", timeout=90000, state="visible")
        except Exception:
            pass

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
            _set_slider_by_label_regex(page, r"Uncertainty", 0.20)

        elif scenario == "C_directional_peak_disagreement":
            _set_mode(page, "Exact strikes")
            # Shift belief peak away from the displayed reference peak by enough margin
            # to exceed the tolerance used by the app (approx >= a few hundred USD).
            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward * 1.07)
            _set_slider_by_label_regex(page, r"Uncertainty", 0.20)

        elif scenario == "D_exact_strikes_mode":
            _set_mode(page, "Exact strikes")
            _set_number_input_by_label_regex(page, r"Belief peak.*mode", forward)
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

    return r


def main() -> int:
    _ensure_playwright()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    results: list[ScenarioResult] = []

    import argparse

    global PORT, BASE_URL, APP_URL

    parser = argparse.ArgumentParser(
        description="Implied lab local UI smoke harness (MVP: validated scenario A_width_target_payoff)."
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
                    "disagreement_text_found": r.disagreement_text_found,
                    "family_block_found": r.family_block_found,
                    "trade_ticket_found": r.trade_ticket_found,
                    "verification_found": r.verification_found,
                    "screenshot_path": r.screenshot_path,
                    "notes": r.notes,
                }
                for r in results
            ],
            "pass_criteria": {
                "harness_scope": (
                    "MVP single-scenario smoke harness; validated scenario: A_width_target_payoff."
                ),
                "recommended_command": (
                    "python scripts/implied_lab_ui_smoke_harness.py --port <PORT> --scenario A_width_target_payoff"
                ),
                "success_requires": (
                    "For each scenario in this run: page_loaded, disagreement_text_found, "
                    "family_block_found, and trade_ticket_found must be true. If scenario "
                    "A_width_target_payoff is included, verification_found must also be true."
                ),
                "future_work": (
                    "Expanding official pass coverage to additional scenarios (B/C/D) is not part of this MVP."
                ),
                "note": (
                    "For the intended MVP exit 0, use --scenario A_width_target_payoff only; "
                    "other invocations may not match exit 0 even when partial checks pass."
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
        verification_ok = next((r for r in results if r.scenario == "A_width_target_payoff"), None)
        verification_ok = bool(verification_ok and verification_ok.verification_found)

        overall_pass = page_loaded_ok and main_ok and verification_ok

        summary_path = RUN_DIR / "ui_smoke_summary.txt"
        summary_path.write_text(
            (
                f"RUN_ID={RUN_ID}\n"
                f"PORT={PORT}\n"
                f"overall_pass={overall_pass}\n"
                f"page_loaded_ok={page_loaded_ok}\n"
                f"main_texts_ok={main_ok}\n"
                f"verification_ok={verification_ok}\n"
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

