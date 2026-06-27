# Cross-venue arb charter v1 — SELECTION

**COMPLETE** 2026-06-26 — scan/backtest auto-run when idle (`sideChannel: true`). No operator SELECT.

[`ppe_propagate_queue.py`](../../scripts/ppe_propagate_queue.py) promotes rows when manifest idle and queue has no READY work. Main-track relay wins when READY.
