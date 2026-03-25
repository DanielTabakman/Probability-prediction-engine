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
