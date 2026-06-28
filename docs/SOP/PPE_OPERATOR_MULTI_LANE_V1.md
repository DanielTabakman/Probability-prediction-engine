# PPE operator multi-lane v1 (design)

**Status:** chartered — see [`SPRINT_PPE_OPERATOR_MULTI_LANE_V1.md`](SPRINT_PPE_OPERATOR_MULTI_LANE_V1.md).

One VM loop driver; `ACTIVE_IDE_SLANES.json` for per-lane checkout; one rotating `what's next?` Cursor thread.

**Pre-charter shipped:** `suggest_thread_rotate` in `ppe_operator_status.py` + thread rotation rules in `agent-continuity.mdc`.
