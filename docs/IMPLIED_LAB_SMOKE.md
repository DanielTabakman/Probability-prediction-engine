# Implied lab — manual smoke checklist (Stabilization S0)

Run the app in **Full** view with Deribit loaded, then **Run implied distribution & strategies**.

If anything fails, use **Debug (last error)** (collapsed expander under the failure caption) and copy type, message, and traceback.

| # | Check | Pass? |
|---|--------|-------|
| 1 | **Chart visible** — Plotly figure (purple lognormal; orange market-implied if data allows) | |
| 2 | **Summary visible** — Right-column summary card (strategy name, debit/credit, cost, max gain/loss, breakevens) | |
| 3 | **Exact strikes** — Mode = Exact strikes; adjust K1–K4; green payoff updates | |
| 4 | **Target payoff** — Mode = Target payoff; payoff sliders update solved shape / summary | |
| 5 | **Belief off** — “Show my belief curve” unchecked → no teal line | |
| 6 | **Belief on** — Checked → teal “My belief” line; peak/width sliders move the curve | |
| 7 | **Expiry switch** — Change expiry; chart and controls stay coherent, no generic failure caption | |

**Note:** This checklist does not change product behavior; it is for manual regression testing after edits to `app.py` / `implied_lab_*`.
