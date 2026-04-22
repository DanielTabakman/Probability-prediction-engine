# Implied lab — manual smoke checklist (Stabilization S0)

**Operator runbook (preflight, Tier 1 vs smoke C, artifacts, closeout, escalation):** `docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md`.

Run the app in **Full** view with **Bitcoin view** enabled. The implied distribution and strategy section loads on its own (Deribit expiries/marks for the lab are fetched when that section runs). **Optional** chart overlays (forward curve, spread overlays, reference tables) appear after **Refresh priced inputs (Deribit)** in the sidebar.



If anything fails, use **Debug (last error)** (collapsed expander under the failure caption) and copy type, message, and traceback.



| # | Check | Pass? |

|---|--------|-------|

| 0 | **Initial auto-load** — Implied probability distribution subheader and controls appear without clicking a separate “run” button; spinners may show while expiries/marks load | |

| 1 | **Chart visible** — Plotly figure (purple lognormal; orange market-implied if data allows) | |

| 2 | **Summary visible** — Right-column summary card (strategy name, debit/credit, cost, max gain/loss, breakevens) | |

| 2a | **Trust / provenance (Sprint 006)** — Immediately under Summary: as-of (UTC), sources, overlay basis, illustrative-scope line from `verification_summary`, pointer to **Verification**; no need to expand **Verification** to see this strip | |

| 2b | **Trade ticket path (Sprint 007)** — After **Belief vs market — at a glance**, **Trade ticket (copy/paste)** is a single top-level expander (not nested under **Strategy details**); **Decision-ready review** text names glance then ticket; caption stays non-advisory | |

| 3 | **Exact strikes** — Mode = Exact strikes; adjust K1–K4; green payoff updates | |

| 4 | **Target payoff** — Mode = Target payoff; payoff sliders update solved shape / summary | |

| 5 | **Belief off** — “Show my belief curve” unchecked → no teal line | |

| 6 | **Belief on** — Checked → teal “My belief” line; peak/width sliders move the curve | |

| 7 | **Expiry switch** — Change expiry; chart and controls stay coherent, no generic failure caption | |

| 8 | **Verification** — Expand **Verification** (under chart/belief); data sources, as-of, density (call count + Breeden status), and strategy notes render | |

| 9 | **Refresh priced inputs** — Click **Refresh priced inputs (Deribit)**; rerun completes; belief slider values unchanged; verification as-of updates | |



**Note:** This checklist does not change product behavior; it is for manual regression testing after edits to `app.py` / `implied_lab_*`.

## Automated local UI smoke harness (narrow coverage)

**Validation classification (SOP):** `python -m pytest -q` is **deterministic** (local). This harness is **live-data-sensitive** (Deribit/Yahoo/spot paths) and **environment-sensitive** (Playwright, network, free ports). Label pass/fail accordingly so operational issues are not read as product regressions; see `docs/SOP/OPERATING_RULES.md` (Execution step discipline → RULE 4).

This is a **narrow-coverage** headless smoke harness—not a full scenario matrix. **`A_width_target_payoff`** is the **default primary** automated path for sprint closeout (see `docs/SOP/OPERATING_RULES.md` → **Validation tiers**). **`C_directional_peak_disagreement`** is a **conditional** gate: **required** when work materially touches disagreement classification, width/peak scenario behavior, belief/disagreement derivation, or related harness logic; **supporting/optional** for presentation or review-only changes unless the sprint spec names **C**. It is **not** a universal closeout requirement for every sprint. Before any smoke run, use the short **preflight hygiene** checklist in **OPERATING_RULES.md** (clean instance, fresh port, avoid orphan processes and manual+smoke collisions). Run **C** explicitly and use the run’s manifest booleans; treat it as “green” only when those checks pass (see `pass_criteria`). Other harness scenarios (`B_peak_aligned`, `D_exact_strikes_mode`) are ad-hoc.

### Required dependencies
- Python deps: `pip install -r requirements.txt` (includes `playwright`)
- Playwright browser:
  - `python -m playwright install chromium`
- Unit tests (local): `pytest` must be installed for `python -m pytest -q`
  - Install: `python -m pip install pytest`
- Network: Yahoo and (for the implied lab) Deribit option marks/expiries must be reachable for a realistic run.
  - **Operational caveat (live-data flakiness):** if spot/quotes are unavailable, the app may display **"Need BTC spot price for implied distribution"** and the belief/disagreement UI may not mount; treat this as **environment/data availability**, not automatically a product regression.

### Command (supported runs)

**One command from repo root** (recommended): picks a free local port automatically and runs the official **`A_width_target_payoff`** path only. The wrapper does not add scenarios or change what that command’s “green” means. Validating **`C_directional_peak_disagreement`** requires invoking the harness with `--scenario C_directional_peak_disagreement` (see below).

`python scripts/run_implied_lab_ui_smoke.py`

**Workflow-Hardening-Slice003 (evidence plane):** the harness manifest includes `slice003_witness` on each scenario row and top-level `workflow_hardening_slice003_closeout` (`evidence_plane_complete`, `workflow_hardening_slice003_signal`, `bounded_live_data_miss`). A healthy width_vol strip run also drops `A_width_target_payoff_slice003_witness.png` beside the main scenario screenshot.

Using the project venv’s interpreter is fine, for example:

`".venv\Scripts\python.exe" scripts\run_implied_lab_ui_smoke.py`

**Explicit harness** (choose a free `--port` yourself):

`A_width_target_payoff`:

`".venv\Scripts\python.exe" scripts\implied_lab_ui_smoke_harness.py --port 8610 --scenario A_width_target_payoff`

`C_directional_peak_disagreement`:

`".venv\Scripts\python.exe" scripts\implied_lab_ui_smoke_harness.py --port 8610 --scenario C_directional_peak_disagreement`

Use a different `--port` if `8610` is busy.

### Artifacts
- Screenshots + JSON manifest: `artifacts/ui_smoke/<run_id>/`
- Manifest file: `artifacts/ui_smoke/<run_id>/ui_smoke_manifest.json`

### What success means today
For **A**, the harness checks page load plus disagreement/family/trade text and Verification (including disagreement classification). For **C** (when you run it), the same base checks apply plus **Directional** in the disagreement line and the manifest’s C-specific booleans. Exit code `0` means the checks required for the scenarios **in that run** passed (see `pass_criteria` in the manifest).

**Sprint 006 note (trust strip vs screenshot):** Scenario **A** expands **Verification** and scrolls to disagreement classification before the `full_page=False` capture, so the default **A** PNG may **not** show the compact **Trust / provenance** block under **Summary**. Use checklist row **2a** (scroll up in the right column) or an ad-hoc screenshot when you need pixel evidence of the strip.

**Sprint 007 note (glance + trade ticket vs screenshot):** The harness still sets `trade_ticket_found` when the label **Trade ticket (copy/paste)** is present in the DOM (may be below the viewport). The default **A** PNG often frames **Decision-ready review** (updated linkage: glance then ticket) but may **not** show the glance card or the ticket expander. Use checklist row **2b** (scroll the right column after review) or an ad-hoc screenshot for pixel evidence of the flatter path.

**Feature slice 008 closeout (2026-04-11, presentation-only):** **Smoke C** not required. Accepted evidence: `python -m pytest -q` → **36** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260411_131344/ui_smoke_manifest.json`, screenshot `artifacts/ui_smoke/20260411_131344/A_width_target_payoff.png`. **Harness stability note:** the primary scenario waits on the exact string **My belief vs market** (the left-column expander label). UI copy that repeats that exact phrase *before* the expander mounts can cause a **false early match** or confusing runs—keep orientation text distinct from the expander title, or scope waits in future harness work. **Operational note:** a **timeout** on a given run is consistent with **network / Deribit** flakiness; classify as **environment-sensitive** and retry with preflight hygiene (`docs/SOP/OPERATING_RULES.md`).

**Scenario sensitivity (Sprint 005 closeout, 2026-04-10):** **C** can **fail** when live marks + default belief inputs yield **mixed** or **width_vol** disagreement (e.g. `width_band=wider`) even though the page loads and disagreement UI is coherent. Classify as **live-data-sensitive** / **scenario-sensitive** — not automatically a regression in the **Decision-ready review** block or digest copy. Prior green **C** artifacts (e.g. `artifacts/ui_smoke/20260410_150352/`) remain valid historical evidence.

### Evidence snapshot (post–Sprint 002 closeout; 2026-04-09)
- Tests: `python -m pytest -q` → **PASS**
- Smoke A: `python scripts/run_implied_lab_ui_smoke.py` → **PASS**
  - Example artifacts: `artifacts/ui_smoke/20260409_120856/` (manifest + `A_width_target_payoff.png`)
- Smoke C: `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port 8512` → **PASS**
  - Example artifacts: `artifacts/ui_smoke/20260409_122715/` (manifest + `C_directional_peak_disagreement.png`)
  - Note: Earlier closeout reruns failed when the belief σ slider could not be set finely enough to keep width-band “similar”; harness now steers σ with finer precision and records disagreement diagnostics when failing.

### Future work
- Broadening to a full scenario matrix or promoting B/D to first-class gates is optional follow-up.


