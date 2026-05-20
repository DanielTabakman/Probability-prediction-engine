# MVP1 disagreement / candidate strip polish — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 4.  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION prep:** [`POST_MVP1_ONBOARDING_HOW_IT_WORKS_SELECTION.md`](POST_MVP1_ONBOARDING_HOW_IT_WORKS_SELECTION.md) (first deferred candidate).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Polish the **disagreement → candidate** strip (width_vol and directional/mixed) with clearer labels, trust-aligned language, explicit falsification, and reinforced **fit vs recommendation** copy — **without** changing disagreement classification rules, thresholds, or core derivation math.

---

## Sprint-level acceptance

1. **`python -m ruff check src tests scripts`** and **`python -m pytest -q`** green after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs recorded in [`MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`](MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md).
3. On chapter closeout: `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) + [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) updated via relay closeout (no hand-edits during BUILD).

---

## Not now

- Feedback / beta instrumentation (§15B slice 6) — separate chapter unless SELECTION merges it.
- Unified chart plan ([`docs/CHART_UNIFIED_PLAN.md`](../CHART_UNIFIED_PLAN.md)).
- MVP1-Phase5-Slice002 (SQLite FK / review horizon UX).
- Changes to `classify_disagreement`, width ratios, or Breeden engine.

---

## Slice map

### MVP1-DisagreementStrip-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-20 — sprint spec, relay JSON, evidence file, frontier queue aligned.

### MVP1-DisagreementStrip-Product-Slice002 — strip polish (PRODUCT) — **CLOSED**

**Closed** 2026-05-20 — provenance payloads + `app_panels` strip chrome + unit tests.

### MVP1-DisagreementStrip-Smoke-Slice003 — dual smoke (CONTROL) — **CLOSED**

**Closed** 2026-05-20 — dual smoke `20260520_050337` + `20260520_050357`.

### MVP1-DisagreementStrip-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-20 — frontier, handoff, integrated status, continuity brief, POST selection prep (completed row).

---

## Manual checklist (PRODUCT)

- Default MVP1 lab (`PPE_POST_MVP1_LAB_UI` off): with belief settings that yield **width_vol**, confirm strip title/caption read clearly; **Verification** row still matches category.
- Same for **directional** / **mixed**.
- With `PPE_POST_MVP1_LAB_UI=1`: strips still appear and copy remains non-advisory.
- Confirm no forbidden phrasing per [`docs/SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md).

---

## Sprint status

**COMPLETE** 2026-05-20.
