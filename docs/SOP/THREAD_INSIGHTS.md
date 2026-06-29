# Thread insights

**Purpose:** Audit trail of context-closeout captures — every item is actionable (no passive `log`).

| Command | Action |
|---------|--------|
| `context_window_closeout.cmd --record --capture` | Closeout + apply pending capture file |
| `python scripts/ppe_thread_capture.py apply --file <json>` | Route a capture file only |
| `python scripts/ppe_thread_capture.py rules` | One-line routing rules |
| `python scripts/ppe_thread_capture.py summary --file <json>` | Numbered operator summary |

**Machine source:** [`THREAD_INSIGHTS.json`](THREAD_INSIGHTS.json) · **Showing:** 0 most recent

> **Routing:** ship_now · triggered · human · build · drop

_No insights captured yet._

## Changelog

| 2026-06-29 | Remove log route; mandatory numbered closeout summary |
