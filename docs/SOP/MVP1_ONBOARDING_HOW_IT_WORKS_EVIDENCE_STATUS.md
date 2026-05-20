# MVP1 onboarding / How it works — evidence status

**Chapter:** [`SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md`](SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md) · **SELECTION:** [`POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md`](POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md)

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **178** passed (2026-05-20) |
| Dual smoke | **PASS** | `20260520_042057` + `20260520_042128` (~127s) |

---

## Product delta

- **`render_how_it_works_expander()`** — [`src/viz/tutorial.py`](../../src/viz/tutorial.py): collapsed-by-default **How this lab works (~90 sec)** expander (§15B slice 5 copy: market-implied, belief overlay, disagreement, strategy families as *fit*, no-advice boundary).
- **`src/viz/app.py`** — expander mounted under **Bitcoin implied lab** header (after read-order caption).

---

## Control charter (witness)

**`MVP1-OnboardingHowItWorks-Control-Slice001`** — **CLOSED** 2026-05-20.

- Verified alignment among [`SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md`](SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md), [`PHASE_PLANS/mvp1_onboarding_how_it_works_relay.json`](PHASE_PLANS/mvp1_onboarding_how_it_works_relay.json), [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md), and this evidence file.
- Baseline reference: `main` @ `2c0393e`+ (post–SELECTION merge **#13**).

---

## Chapter status

**IN PROGRESS** — Product-Slice002 + Smoke-Slice003 **CLOSED** 2026-05-20. **Next:** `MVP1-OnboardingHowItWorks-Closeout-Slice004` (chapter close / steward).
