# Steward operator v1 — human commitments (real-world work)

**Plane:** CONTROL-PLANE · **Purpose:** cue **you** (not agents) on tester sessions, validation evidence, and VPS follow-ups.

**Automation:** [`ppe_steward_scoreboard.py`](../../scripts/ppe_steward_scoreboard.py) · [`ppe_steward_nudge.py`](../../scripts/ppe_steward_nudge.py)  
**Calendar:** [`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md) · **Playbook:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)

---

## Two ntfy channels (do not mix)

| Channel | Env var | Job | Commands? |
|---------|---------|-----|-----------|
| **Operator** | `PPE_NTFY_TOPIC` | Loop, IDE_BUILD, build/fix | Yes (`build`, `status`, …) |
| **Steward** | `PPE_NTFY_STEWARD_TOPIC` | Mon/Thu “what to do next” | **No** — receive only |

Same ntfy app → **two subscriptions**, two private topic names.

---

## What you need to succeed

Minimum stack — if any is missing, nudges won’t convert to evidence:

| # | Requirement | Why |
|---|-------------|-----|
| 1 | **`PPE_NTFY_STEWARD_TOPIC`** set + subscribed in ntfy app | Without this, zero cues |
| 2 | **Desktop awake** at Mon 13:00 + Thu 20:00 local (or run scoreboard manually those days) | Task Scheduler only fires when PC is on |
| 3 | **3 names** on a short outreach list (BTC options / quant-curious) | Mon nudge fails if you have to “find someone” first |
| 4 | **Demo works once** — run [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) solo on `marketstructureos.com` | Broken URL wastes sessions |
| 5 | **20–30 min calendar block** between Mon and Thu | One session per week minimum |
| 6 | Know the **receipt file**: [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) § MSOS P8 | Thu nudge is useless if you don’t log the row |

**Weekly success = two tiny actions:**

- **Monday:** one outreach text + calendar hold (5 min)
- **Thursday:** one table row OR one-line skip reason (5 min)

Optional but high leverage: run `python scripts/ppe_steward_scoreboard.py` before Mon outreach.

---

## If you fail — most likely causes

| Symptom | Most likely cause | Fix |
|---------|-------------------|-----|
| No phone ping Mon/Thu | Desktop off/asleep; steward topic unset | Never sleep when plugged in; `--steward-test` |
| Ping arrives, score still 0/10 | Session happened but **no row logged** | Thu: paste row in VALIDATION_REALITY_CHECKS (5 min) |
| Outreach never sent | Treated nudge as “think about validation” not “send one text” | Mon: literal SMS to one name — no prep |
| Testers confused in session | Demo not rehearsed; wrong URL | Solo run DEMO_OPERATOR_SCRIPT once first |
| “I’ll do it when product is ready” | Waiting on **agents** for **human** gate | Agents pause until **you** log 10 rows + COMPLETE report |
| Muted / ignored steward topic | Alert fatigue from operator topic | Keep steward subscription **unmuted**; operator can snooze |
| Perfectionism — no “good enough” testers | Friends-first cohort never starts | First 3 sessions can be smart non-experts; log honestly |

**Honest skip beats silent drift:** `Skipped week of YYYY-MM-DD — reason` still counts as steward receipt.

---

## One-time setup (~5 min)

1. **Pick a steward topic** — e.g. `ppe-yourname-steward-<secret>`.
2. **ntfy app** → Subscribe to that topic (separate from operator topic).
3. **Edit** `ppe_operator_notify.local.cmd` (copy from `.example` if needed):

```bat
set "PPE_NTFY_TOPIC=ppe-yourname-operator-<secret>"
set "PPE_NTFY_STEWARD_TOPIC=ppe-yourname-steward-<secret>"
```

4. **Verify:**

```bat
python scripts\ppe_notify_push.py --steward-check
python scripts\ppe_notify_push.py --steward-test
```

5. **Schedule nudges** (desktop, local time):

```bat
install_steward_nudge_task.cmd
```

Defaults: **Mon 13:00** (plan outreach) · **Thu 20:00** (log or skip).  
Re-run after changing days — removes legacy Wed/Sun tasks if present.

Custom times:

```powershell
powershell -File scripts\install_steward_nudge_task.ps1 -RepoRoot . -MonRunTime 09:00 -ThuRunTime 17:30
```

---

## What you do when a nudge fires

### Monday — plan outreach

1. Open scoreboard (optional):

```bat
python scripts\ppe_steward_scoreboard.py
```

2. **Pick one person** from your list.
3. **Send a short text** — “20 min this week to walk through our BTC options research demo?”
4. **Book a slot** — calendar hold counts; no repo row yet.

### Thursday — log or skip

**If you ran a session:**

1. Open [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) — you already used this live.
2. Add **one row** in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) § **MSOS P8 friends-first tester metrics** (replace `_fill_`):

| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | Return to monitor/history | Paid interest (steward call) | Notes |
|------|----------------|------------------------|----------------------|---------------------------|------------------------------|-------|
| 2026-06-12 | _name / role_ | Y/N | Y/N | Y/N | Y/N | _1-line note_ |

3. Commit or leave for next agent pass — row must exist in repo for scoreboard to count it.

**If you skipped:**

Add a short note: `Skipped week of YYYY-MM-DD — reason`.

---

## Scoreboard (anytime)

```bat
python scripts\ppe_steward_scoreboard.py
```

Example output:

```text
Tester sessions: 0/10 (10 remaining)
This week (Mon–Sun): 0 logged
Validation report: DRAFT

Do next:
1. Book 1 guided tester call this week ...
2. Run demo: open docs/SOP/DEMO_OPERATOR_SCRIPT.md ...
3. After session: add one row in VALIDATION_REALITY_CHECKS.md ...
```

JSON for scripts: `python scripts\ppe_steward_scoreboard.py --json`

---

## What unlocks the build pipeline

| Evidence | File | Effect |
|----------|------|--------|
| **10 logged sessions** | `VALIDATION_REALITY_CHECKS.md` § MSOS P8 | Credible cohort for report |
| **Report COMPLETE** | `MSOS_P8_VALIDATION_REPORT_V1.md` header | Auto-select / propagate gate opens |
| **Paid interest Y** | Honest steward conversation only | Playbook commercial fork input |
| **VPS CTA live** | `COMMERCIAL_OPS_COMPLETION.md` | Public demo + research beta |

Until report is **COMPLETE**, agents stay on wedge proof unless backlog row has `urgent: true`.

---

## Manual test (before waiting for Mon/Thu)

```bat
python scripts\ppe_steward_nudge.py --dry-run --slot monday
python scripts\ppe_steward_nudge.py --slot monday --force
```

`--force` bypasses once-per-week dedup (for testing only).

---

## Related

- [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md) — operator topic + phone commands
- [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — session log
- [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) — rollup + SELECTION

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-12 | v1 — steward topic, scoreboard, Mon/Thu nudges |
| 2026-06-12 | Success prerequisites + failure modes; Wed/Sun → Mon/Thu |
