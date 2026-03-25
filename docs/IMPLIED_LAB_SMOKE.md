# Implied lab — manual smoke checklist (Stabilization S0)



Run the app in **Full** view with **Bitcoin view** enabled. The implied distribution and strategy section loads on its own (Deribit expiries/marks for the lab are fetched when that section runs). **Optional** chart overlays (forward curve, spread overlays, reference tables) appear after **Refresh priced inputs (Deribit)** in the sidebar.



If anything fails, use **Debug (last error)** (collapsed expander under the failure caption) and copy type, message, and traceback.



| # | Check | Pass? |

|---|--------|-------|

| 0 | **Initial auto-load** — Implied probability distribution subheader and controls appear without clicking a separate “run” button; spinners may show while expiries/marks load | |

| 1 | **Chart visible** — Plotly figure (purple lognormal; orange market-implied if data allows) | |

| 2 | **Summary visible** — Right-column summary card (strategy name, debit/credit, cost, max gain/loss, breakevens) | |

| 3 | **Exact strikes** — Mode = Exact strikes; adjust K1–K4; green payoff updates | |

| 4 | **Target payoff** — Mode = Target payoff; payoff sliders update solved shape / summary | |

| 5 | **Belief off** — “Show my belief curve” unchecked → no teal line | |

| 6 | **Belief on** — Checked → teal “My belief” line; peak/width sliders move the curve | |

| 7 | **Expiry switch** — Change expiry; chart and controls stay coherent, no generic failure caption | |

| 8 | **Verification** — Expand **Verification** (under chart/belief); data sources, as-of, density (call count + Breeden status), and strategy notes render | |

| 9 | **Refresh priced inputs** — Click **Refresh priced inputs (Deribit)**; rerun completes; belief slider values unchanged; verification as-of updates | |



**Note:** This checklist does not change product behavior; it is for manual regression testing after edits to `app.py` / `implied_lab_*`.

## Automated local UI smoke harness (MVP)

This is a **single-scenario MVP** headless smoke harness. The only scenario validated end-to-end for the current pass definition is **`A_width_target_payoff`**. Running other scenario names is reserved for **future work** (not part of the official MVP pass).

### Required dependencies
- Python deps: `pip install -r requirements.txt` (includes `playwright`)
- Playwright browser:
  - `python -m playwright install chromium`
- Network: Yahoo and (for the implied lab) Deribit option marks/expiries must be reachable for a realistic run.

### Command (supported MVP run)
From the project folder, using the project venv:

`".venv\Scripts\python.exe" scripts\implied_lab_ui_smoke_harness.py --port 8610 --scenario A_width_target_payoff`

Use a free `--port` if `8610` is busy.

### Artifacts
- Screenshots + JSON manifest: `artifacts/ui_smoke/<run_id>/`
- Manifest file: `artifacts/ui_smoke/<run_id>/ui_smoke_manifest.json`

### What success means today (MVP)
For **`A_width_target_payoff`** only, the harness checks that the page loaded and that DOM checks find: disagreement text, strategy-family block, trade ticket, and Verification content (including disagreement classification). Exit code `0` means those checks passed for the scenarios in that run (see `pass_criteria` in the manifest).

### Future work
- Expanding automated coverage to additional scenarios (e.g. B/C/D) and tightening manifest wording for multi-scenario runs is **not** part of this MVP harness yet.


