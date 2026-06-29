# Exposure menu v1 — SELECTION

**Chapter:** `ppe_exposure_menu_v1`  
**Module:** `exposure_menu` (class `EXPOSURE_PATH`)  
**Program:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_exposure_menu_v1_relay.json`](PHASE_PLANS/ppe_exposure_menu_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_EXPOSURE_MENU_V1.md`](SPRINT_PPE_EXPOSURE_MENU_V1.md)  
**Validation hook:** [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md)

---

## Status

**SELECTED** 2026-06-29 — operator-approved relay; **P1 side channel** (trader workflow front door). Deferred BL density smoothing.

**First slice:** `PPE-ExposureMenu-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Customer signal | NVIDIA LEAPS prospect wanted help getting exposure without manual chain sift |
| Product gap | Strategy Lab is thesis/disagreement-first; Expression planner is options-structure-only — neither answers “how do I get long NVDA?” |
| Architecture | New module `exposure_menu` — own route `/exposure`, own entity `ExposurePath`, reuses fetch/cache underneath |
| Milestone fit | Trader Workflow Integration — simpler entry before Strategy Lab |
| Priority | P1 — not P0; does not preempt active horizon replay charter |

**Blocked until:** ~~tradeable universe + NVDA live~~ **satisfied**.

---

## Acceptance (chapter)

1. `python scripts/find_exposure_paths.py --asset NVDA --direction long --json` returns ≥3 **Live** paths (spot + ≥2 options) or honest `insufficient_chain`.
2. Same CLI for `--asset BTC --direction long`.
3. `GET /ppe-display-api/exposure-menu.json?asset=NVDA&direction=long` matches CLI contract.
4. MSOS `/exposure` — picker + direction + card grid; secondary nav link.
5. Planned rails (`perp`, `etf_proxy`) render as **Planned** — no fake premiums.
6. Footer + `recommendation_status: path_not_recommendation` on every path.
7. Evidence doc COMPLETE; module registry + HTML map updated.

---

## Non-goals

- Natural language intake
- Workflow save / monitor hook (T4 defer)
- Full enabled-universe rollout (NVDA + BTC proof only)
- Live execution
- Merging UI into Strategy Lab

---

## Next chapter (same program, defer)

`ppe_exposure_menu_universe_v1` — all enabled registry assets; `ppe_exposure_menu_nl_v1` — phrase intake.
