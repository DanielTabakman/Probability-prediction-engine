# MVP1 post-Phase3 steering + smoke witness — evidence status

**Chapter:** MVP1 post-Phase3 steering + smoke witness refresh (v0)  
**Status:** **IN PROGRESS**  
**SELECTION:** [`POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md`](POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md)  
**Sprint spec:** [`SPRINT_MVP1_POST_PHASE3_STEERING_SMOKE.md`](SPRINT_MVP1_POST_PHASE3_STEERING_SMOKE.md)  
**Phase plan:** [`PHASE_PLANS/mvp1_post_phase3_steering_smoke_relay.json`](PHASE_PLANS/mvp1_post_phase3_steering_smoke_relay.json)

---

## Witness log

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-PostPhase3-Control-Slice001 | **OPEN** | charter witness (prior relay pass) |
| MVP1-PostPhase3-Smoke-Slice002 | **CLOSED** 2026-05-28 | dual smoke witness on `main` @ `b4b195b` |
| MVP1-PostPhase3-Closeout-Slice003 | **OPEN** | chapter close |

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **227** passed (2026-05-28, Smoke-Slice002) |
| Dual smoke | **PASS** | `scripts/run_mvp1_dual_implied_lab_smoke.py` exit **0** |

---

## Smoke-Slice002 witness (dual implied-lab)

| Run ID | Scenario | Exit | verification | Notes |
|--------|----------|------|--------------|-------|
| 20260528_123049 | MVP1_compact_verification | 0 | true | ~765s; trust_strip + product_shell + decision_review |
| 20260528_124335 | A_width_target_payoff | 0 | true | ~193s; `PPE_POST_MVP1_LAB_UI=1` |

**Dual smoke total:** ~959s (wrapper re-run after transient A_width flake on first attempt).

**Manifests:** `artifacts/ui_smoke/20260528_123049/ui_smoke_manifest.json`, `artifacts/ui_smoke/20260528_124335/ui_smoke_manifest.json`

**Screenshots:** `artifacts/ui_smoke/20260528_123049/MVP1_compact_verification.png`, `artifacts/ui_smoke/20260528_124335/A_width_target_payoff.png`
