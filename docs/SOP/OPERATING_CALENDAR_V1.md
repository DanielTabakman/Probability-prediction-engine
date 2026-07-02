# Operating calendar v1

**Purpose:** Light cadence for a real-company operating rhythm — without agent overload. **Calendar doc only**; automation does not schedule these events.

**Founder surface:** [`FOUNDER_OPERATOR_SURFACE_V1.md`](FOUNDER_OPERATOR_SURFACE_V1.md) · **Collaboration pulses:** [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) — agents must not paste these rows as founder todo lists in unrelated threads.

**Strategic canon:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) · **Validation rollup:** [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md)

**Cadence tags:** `founder` = judgment or external world · `agent` = operator/charter thread runs and reports · `digest-only` = Monday ntfy; no action unless founder opts in

---

## Daily (automated — founder read optional)

| Layer | When | Artifact |
|-------|------|----------|
| **L1 Morning** | ~08:00 local ntfy | `scripts/ppe_morning_report.py` · `ppe_founder_pulse.cmd --layer morning` |
| **L3 Alert** | Immediate on stall | `ppe_founder_pulse.cmd --layer alert --write --notify` |

See [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) for L2 completion and L4 weekly.

---

## Weekly (~30 min founder time)

| Tag | Task | Artifact |
|-----|------|----------|
| `digest-only` | **L4 Weekly** systems pulse | `weekly_digest_monday.cmd` · [`WEEKLY_DIGEST.md`](../RELEASES/WEEKLY_DIGEST.md) |
| `founder` | 1–2 tester sessions OR log why skipped | [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) |
| `agent` | Check loop verdict | Operator thread: `what's next?` or `run_ppe_operator.cmd --brief` → `OPERATOR_GUARD_REPORT.md` |
| `digest-only` | Scan **human steward backlog** (policy topics) | [`HUMAN_STEWARD_BACKLOG.md`](HUMAN_STEWARD_BACKLOG.md) · Monday ntfy digest — deep work only on monthly steward pass |
| `founder` | VPS / research beta CTA if still pending | [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) |

**Agents:** run `agent`-tagged rows in operator thread; do not append calendar to every reply.

**Monday ntfy (one-time on loop host VM):** `powershell -File scripts\install_weekly_digest_task.ps1 -RepoRoot "%CD%"` — runs `weekly_digest_monday.cmd` (radar + digest + human backlog titles).

---

## Monthly (~45 min — founder charter pass)

Open a **founder charter** thread ([`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md)); agents draft, founder decides.

### Founder collaboration review (~15 min of the pass)

| Tag | Task | Artifact |
|-----|------|----------|
| `founder` | Did L1/L3/L4 pulses feel honest this month? | [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) § Ongoing integration |
| `founder` | One charter tweak if agents hid stalls or asked technical forks | Same doc — changelog |
| `agent` | Write `FOUNDER_PULSE_LAST.json` sample if asked | `ppe_founder_pulse.cmd --layer weekly` |

---
| Tag | Task | Artifact |
|-----|------|----------|
| `founder` | Confirm playbook **Current stage** table is honest | [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — agent may draft update |
| `agent` | Review backlog rows — tier + priority still honest | [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) + [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md) |
| `founder` | **Human steward backlog** — pick one policy/architecture topic | [`HUMAN_STEWARD_BACKLOG.md`](HUMAN_STEWARD_BACKLOG.md) |
| `founder` | Metrics vs playbook checkpoints (return rate, paid interest) | [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) draft sections |
| `founder` | Log any `urgent: true` bypass — was it justified? | Reality checks or report §3 |

**Agent load:** one founder charter thread; `@FOUNDER_OPERATOR_SURFACE_V1.md` + `@PRODUCT_FOCUS_PLAYBOOK_V1.md` — not every BUILD worker.

---

## Quarterly (half day — founder + agent)

| Tag | Task | Outcome |
|-----|------|---------|
| `founder` | Complete or refresh **validation report** | Status **COMPLETE** or explicit HOLD with rationale |
| `founder` | **Next SELECTION** from report §6 / playbook Q4 fork | Agent queues rows after founder decision |
| `founder` | Milestone review (below) | Agent updates milestone table in this doc |
| `founder` | Defer list audit | Confirm execution / multi-asset / paywall still deferred |

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
- Automatic playbook edits (founder owns mythos updates; agents draft on charter pass)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-12 | v1 — weekly / monthly / quarterly cadence + milestone table |
| 2026-07-01 | Founder/agent/digest-only tags; link FOUNDER_OPERATOR_SURFACE_V1 |
| 2026-07-02 | Daily L1/L3 pulse rows; link FOUNDER_COLLABORATION_CHARTER_V1 |
