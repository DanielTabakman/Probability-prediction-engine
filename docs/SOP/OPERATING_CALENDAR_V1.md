# Operating calendar v1

**Purpose:** Light cadence for a real-company operating rhythm — without agent overload. **Calendar doc only**; automation does not schedule these events.

**Strategic canon:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) · **Validation rollup:** [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md)

---

## Weekly (operator — ~30 min)

| Task | Artifact |
|------|----------|
| 1–2 tester sessions OR log why skipped | [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) |
| Check loop verdict (`run_ppe_operator.cmd --brief`) | `artifacts/orchestrator/OPERATOR_GUARD_REPORT.md` |
| Scan **human steward backlog** (policy topics) | [`HUMAN_STEWARD_BACKLOG.md`](HUMAN_STEWARD_BACKLOG.md) · Monday ntfy digest |
| VPS / research beta CTA if still pending | [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) |

**Agents:** not required unless `IDE_BUILD` / `ERROR`.

---

## Monthly (steward — ~45 min)

| Task | Artifact |
|------|----------|
| Update playbook **Current stage** table | [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) |
| Review backlog rows — tier + priority still honest | [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) + [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md) |
| **Human steward backlog** — pick one policy/architecture topic | [`HUMAN_STEWARD_BACKLOG.md`](HUMAN_STEWARD_BACKLOG.md) · `python scripts/ppe_human_backlog.py --status` |
| Metrics vs playbook checkpoints (return rate, paid interest) | [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) draft sections |
| Log any `urgent: true` bypass — was it justified? | Reality checks or report §3 |

**Agent load:** one steward thread; `@PRODUCT_FOCUS_PLAYBOOK_V1.md` + `@OPERATING_CALENDAR_V1.md` — not every BUILD worker.

---

## Quarterly (steward + operator — half day)

| Task | Outcome |
|------|---------|
| Complete or refresh **validation report** | Status **COMPLETE** or explicit HOLD with rationale |
| **Next SELECTION** from report §6 / playbook Q4 fork | New `PHASE_QUEUE` / backlog rows |
| Milestone review (below) | Update milestone table in this doc |
| Defer list audit | Confirm execution / multi-asset / paywall still deferred |

---

## Milestones (living table)

Update at quarterly review. **Done** = evidence in repo, not aspiration.

| Milestone | Target | Status | Evidence |
|-----------|--------|--------|----------|
| MSOS P0–P8 waterfall shipped | 2026-Q2 | **done** | MSOS evidence docs |
| Product focus playbook + runtime gate | 2026-Q2 | **done** | `ppe_focus_gate.py`, this calendar |
| P8 validation report **COMPLETE** | _date_ | **open** | `MSOS_P8_VALIDATION_REPORT_V1.md` |
| 10 guided tester sessions logged | _date_ | **open** | `VALIDATION_REALITY_CHECKS.md` |
| Paid-interest signal (≥1 honest Y) | _date_ | **open** | reality checks |
| Public research-beta URL live | _date_ | **open** | VPS witness |
| Next chartered chapter from evidence | after report | **open** | SELECTION doc + queue |

---

## What we deliberately do not schedule

- Full playbook paste into IDE BUILD starters (3-line excerpt only)
- Daily agent-driven strategy meetings
- Automatic playbook edits (human/steward owns mythos updates)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-12 | v1 — weekly / monthly / quarterly cadence + milestone table |
