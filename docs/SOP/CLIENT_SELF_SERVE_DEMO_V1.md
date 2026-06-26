# Client self-serve demo v1

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
> **Workstream A** — [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) · relay chapter `msos_self_serve_onboarding_v1`
<!-- ACTIVE_PRODUCT_DIRECTION:END -->

**Purpose:** Prospects and traders use the **public MSOS URL** and **in-app guided tour** without operator hand-holding. Operator-led demos remain optional, not the default onboarding path.

**Relay chapter:** [`POST_MSOS_SELF_SERVE_ONBOARDING_V1_SELECTION.md`](POST_MSOS_SELF_SERVE_ONBOARDING_V1_SELECTION.md) · [`SPRINT_MSOS_SELF_SERVE_ONBOARDING_V1.md`](SPRINT_MSOS_SELF_SERVE_ONBOARDING_V1.md)

---

## Self-serve entry

| Entry | URL / action |
|-------|----------------|
| Public homepage | Production apex — hero CTA → Strategy Lab tour |
| Guided tour | `/strategy-lab?tutorial=1` (force) or first-visit auto-start |
| Beginner copy | `/strategy-lab?tutorial=beginner` |
| Restart tour | Public nav **Restart tour** (clears local completion flag) |
| Skip | Jump to `/strategy-lab` without query param after completion |

**Deploy witness:** [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) · [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md)

---

## Tutorial contract (production)

Any visitor-visible workflow change in MSOS shell **must** update tour steps in the **same PR**:

- [`apps/msos-web/src/lib/platformTutorial.ts`](../../apps/msos-web/src/lib/platformTutorial.ts) — step copy + anchors
- [`data-tour` anchors](../../apps/msos-web/) on Strategy Lab regions
- pytest witnesses in [`tests/test_msos_web_homepage.py`](../../tests/test_msos_web_homepage.py)

Chapter closeout requires evidence checkboxes green in [`MSOS_SELF_SERVE_ONBOARDING_V1_EVIDENCE_STATUS.md`](MSOS_SELF_SERVE_ONBOARDING_V1_EVIDENCE_STATUS.md).

---

## Operator optional path

[`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) remains for high-touch sessions. **Do not** gate self-serve on scheduled operator time.

Log sessions in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — tag `signal:` per [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md).

---

## Non-goals (this workstream)

- Friends-first cohort gating
- Stripe / paid self-serve checkout
- Equity ticker onboarding (deferred — `ppe_equity_options_v1`)
- Full P4→P7 multi-route tour (follow-on in workflow loop fidelity chapter)
