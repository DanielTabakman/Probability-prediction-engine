# HANDOFF

Purpose: minimum context needed for the next work session.

## HANDOFF GATE (fill this block; no interpretation)

Copy/paste and fill every field. Do not infer from memory; verify in repo/docs.

```text
HANDOFF GATE — v3.0 (MVP1 control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > PPE_MASTER_MVP1 > MVP1_FRONTIER > HANDOFF > OPERATING_RULES
- Controlling master canon: `docs/VISION/PPE_MASTER_MVP1.md`
- Live frontier (only steering truth): `docs/SOP/MVP1_FRONTIER.md`
- Active MVP1 focus: **Commercial Validation** — [`SPRINT_POST_VALIDATION_COMMERCIAL.md`](SPRINT_POST_VALIDATION_COMMERCIAL.md) ACCEPTED
- Closed slices (Validation Chapter): Control / Smoke / UX / Deploy / Closeout — **COMPLETE** 2026-05-19
- Closed slices (Commercial Validation): Control / Offer / Reality / Nvidia — **COMPLETE** 2026-05-19
- Current execution focus: **SELECTION** — next roadmap chapter (no BUILD until chartered)
- Next pending execution step: live paid-interest outreach per [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md); re-run dual smoke after deploy
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift; legacy `CURRENT_FRONTIER.md` is **historical only**
- Naming rule: H1/H1-01/H1-02 is non-canonical unless explicitly reintroduced; use Phase/Sprint/Slice
- Canonical truth rule: steering truth lives in canonical docs; repo-state gate is separate

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify at session start (`git rev-parse --abbrev-ref HEAD`)
- Ahead/behind vs origin: verify at session start
- Working tree: verify at session start (CLEAN required before BUILD)
- Untracked canonical docs present? verify; must be NO before accepted baseline
- BUILD allowed right now? verify preflight + clean tree

C) AGENT CONTINUITY (required)
- Safe to switch agents? verify after repo-state
- If YES: branch + HEAD SHA + `MVP1_FRONTIER.md` + active sprint spec
```

**Steward workflow:** [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). **Repo map:** [CODEBASE_MAP.md](CODEBASE_MAP.md). **Implied lab ops:** [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md).

## Execution step rules (inherit from SOP)

Declare **exactly one** execution step type per session (**BUILD**, **CLOSEOUT**, **RECOVERY**, **SELECTION**) per [OPERATING_RULES.md](OPERATING_RULES.md).

## Control-plane safety: doc-state vs repo-state

Report **doc-state** (canonical alignment) and **repo-state** (reproducibility) separately. **`MVP1_FRONTIER.md`** is live steering; this file is minimal handoff only.

## Current priority (MVP1)

**Validation Chapter:** **COMPLETE** (2026-05-19) — [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md), [`SPRINT_VALIDATION_CHAPTER.md`](SPRINT_VALIDATION_CHAPTER.md).

**Commercial Validation:** **COMPLETE** (2026-05-19). **Next:** steward SELECTION for following chapter — see [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).

**Legacy Sprint 004 / `recovery/frontier-steward-v2_1-baseline`:** historical Phase 2 track only; do **not** use for MVP1 Validation execution unless explicitly re-chartered. See [`CURRENT_FRONTIER.md`](CURRENT_FRONTIER.md) supersession note.

## Hard rule reminders

- No execution directly on `main` without steward merge discipline; use short-lived branches.
- Single-plane passes; no untracked `docs/SOP/**` at accepted baselines.
- Dual smoke: `python scripts/run_mvp1_dual_implied_lab_smoke.py` after implied-lab changes.

## Active feature slice

See **`MVP1_FRONTIER.md`** — do not duplicate here.

## Completed recently

Validation Chapter product slices (smoke + UX) and control infra — ledger in `SPRINT_VALIDATION_CHAPTER.md` and `MVP1_FRONTIER.md`.

## Remaining

- See **`MVP1_FRONTIER.md`** Commercial Validation relay queue
- Live **paid-interest** customer signal when outreach runs ([`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md))

## Risks / watchouts

- Prefer `python -m streamlit` if `streamlit` is not on PATH.
- Live-data smoke may degrade when Deribit/Yahoo unavailable — classify per implied-lab runbook §6.
- Playwright, free ports, and localhost reachability for UI smoke.

## Most relevant tests/checks

1. `python -m pytest -q`
2. `python scripts/run_mvp1_dual_implied_lab_smoke.py`
3. `python -m streamlit run src/viz/app.py` — local visual check

## Recommended next step

**SELECTION** — pick next roadmap chapter; run live paid-interest conversation when ready ([`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md)).

## Last updated

2026-05-19 — Commercial Validation chapter closed on `main` (offer surface + operator docs).
