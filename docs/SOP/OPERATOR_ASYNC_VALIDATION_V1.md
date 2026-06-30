# Operator async validation v1

**For:** human operator (solo-first) · **Plane:** CONTROL-PLANE

**Related:** [`OPERATOR_UX_WITNESS_V1.md`](OPERATOR_UX_WITNESS_V1.md) · [`FOUNDER_OPERATOR_CRIB_SHEET_V1.md`](FOUNDER_OPERATOR_CRIB_SHEET_V1.md) · [`STEWARD_VALIDATION_GUIDE_V1.md`](STEWARD_VALIDATION_GUIDE_V1.md)

---

## Why async exists

Live screen-share demos are high pressure and hard to schedule. **Async validation** collects the same signals — comprehension, confusion category, return intent — without you performing on a call.

Use async **by default** while solo. Reserve live sessions for when someone asks for a walkthrough or you want depth on one relationship.

---

## Operator workflow (weekly, ~15 min)

| Step | Action | Time |
|------|--------|------|
| 1 | Send **one** async outreach message (below) | 2 min |
| 2 | Solo UX checklist if MSOS shell changed ([`OPERATOR_UX_WITNESS_V1.md`](OPERATOR_UX_WITNESS_V1.md)) | 5 min |
| 3 | Export feedback: `python scripts/ppe_export_web_feedback.py --markdown` | 1 min |
| 4 | Optional: copy strong rows into [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) | 2 min |

**Inbox (after deploy):** https://marketstructureos.com/operator/feedback — requires Cloudflare Access (`MSOS_OPERATOR_EMAIL` on VPS).

**Public form:** https://marketstructureos.com/feedback — share this link; no login for testers.

---

## Outreach text (async — copy/edit)

```text
Hey [Name] — I built a BTC options research demo (market-implied vs your view). No pitch — explore when you have 5 min, then hit Share feedback on the site (~2 min). Honest reactions from someone who trades options help a lot. https://marketstructureos.com/strategy-lab
```

Follow-up (only if they explored but didn't submit):

```text
If anything confused you, the feedback form is https://marketstructureos.com/feedback — even one line helps.
```

---

## What counts as validation signal

| Signal | Source |
|--------|--------|
| Comprehension / return Y/N | Feedback JSONL or learn debrief submit |
| Confusion category + usefulness | `/feedback` form |
| Solo operator witness | 3-checkbox pass in UX witness doc |
| Live guided session | Still gold standard when you're ready — [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) |

Export script rolls up JSONL; you decide which rows merit a line in reality checks.

---

## Live sessions (when ready)

Not required for async weeks. When you schedule live:

- Phone notebook: https://marketstructureos.com/session.html (operator only — do not share)
- After call: they can still use `/feedback` so you're not the only scribe

---

## Further ideas (not built yet)

- **Email nudge** when new feedback arrives (ntfy hook on JSONL append)
- **Weekly digest** auto-written to `artifacts/validation/web_feedback_weekly.md`
- **Loom optional** — "record your first reaction" link in outreach for traders who prefer video

Park these in operator thread if you want them chartered.
