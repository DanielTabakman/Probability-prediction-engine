# Product focus playbook v1

**Purpose:** Keep MSOS + PPE aligned on **wedge proof** before platform expansion. Use for steward SELECTION, scope fights, and “are we drifting?” checks.

**As-of:** 2026-06-12 · **Review cadence:** monthly steward pass · **Hard gate:** MSOS P8 validation report.

**Related canon (do not duplicate):**

| Doc | Role |
|-----|------|
| [`PRODUCT_THESIS.md`](../PRODUCT_THESIS.md) | Product north star (belief ↔ payoff lab) |
| [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) | MSOS waterfall P0–P8 |
| [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) / [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) | Live BUILD queue |
| [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) | Session + paid-interest log |
| [`STEWARD_VALIDATION_GUIDE_V1.md`](STEWARD_VALIDATION_GUIDE_V1.md) | **Human operator step-by-step** (why + how) |
| [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) | Tactical BUILD compression |
| [`VISION/PHASE_VISION_CURRENT.md`](../VISION/PHASE_VISION_CURRENT.md) | Phase UX / semantic deferrals |

---

## Precedence

| Question | Controlling doc |
|----------|-----------------|
| What slice runs next in relay? | Matching **FRONTIER** (MVP1 or MSOS) |
| Should we add scope / new asset / execution? | **This playbook** + non-widening rule in PPE Master |
| What do we build after P8? | [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) (evidence-based SELECTION) |

When this playbook and a FRONTIER disagree on **BUILD order**, FRONTIER wins for automation. When they disagree on **whether to widen scope**, this playbook wins until the P8 report updates priorities.

---

## One-line north star

**See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds.**

Everything else serves that loop for **10–30 obsessed testers**, not breadth of platform surface.

---

## Current stage (honest)

| Signal | Status |
|--------|--------|
| PPE implied lab (MVP1) | **Shipped** — belief, disagreement, freeze/review, dist stats legibility |
| MSOS shell | **P2–P5 complete**; **P6** in flight; **P7–P8** pre-chartered |
| Paid interest | **N** — [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) |
| VPS / research beta URL | **Pending** — steward parallel ([`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md)) |

**Risk:** Engineering maturity (relay, witnesses, MSOS chapters) can run **ahead of** market pull. This playbook biases **validation over new surface area** until P8.

---

## Priority stack (binding)

Use this order when choosing steward SELECTION or saying no to scope creep.

| Priority | Focus | Why |
|----------|--------|-----|
| **P0 — Wedge proof** | 10–30 BTC options testers; guided sessions; reality-check rows | Coinbase / SpotGamma: one audience, dense usage before scale |
| **P1 — Complete chartered MSOS P6–P8** | Sim-only expression → minimal monitoring → tester release | Program chartered; P8 = PMF gate |
| **P2 — Lab legibility only** | MVP1 slices that improve 15-second comprehension or disagreement clarity | Phase vision; no new math domains |
| **P3 — Distribution** | Dist demo, public URL, fintwit / newsletter partners | Peers spent founder time on distribution comparable to eng |
| **P4 — Monetization signal** | Manual paid pilot / research beta (no billing automation) | SpotGamma subscription before “platform” |
| **Defer** | Execution, Hyperliquid, multi-asset, Polymarket arb, AI assistant, paywall automation | MSOS program + PPE Master non-goals |

---

## 12-month direction (quarters)

### Q1 — Prove the wedge

**Do:** Finish **P6** (sim-only). Run **5–10 guided sessions** on implied lab (Streamlit or MSOS embed). Log every session in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md). Use dist stats / dist demo in every demo.

**Defer:** New assets, execution, control-plane expansion beyond chartered relay.

**Learn from:** Coinbase (forum-era distribution); Plaid (pivot to what integrators pull); SpotGamma (one visual insight).

**Checkpoint (end Q1):** ≥3 of 10 testers return within 7 days without a ping. If not, **pause P7/P8 product work** and SELECTION MVP1 legibility only.

### Q2 — Habit loop

**Do:** **P7** minimal — “did my thesis still make sense?” not full calibration science. Weekly office hours (5–8 testers). Instrument: open lab → set belief → save/freeze.

**Defer:** Undefined thesis-health metrics; backend persistence until pull proves it.

**Learn from:** PayPal (users hacked product for eBay); OptionStrat (free tool → habit).

**Checkpoint:** ≥40% WAU among cohort; thesis confirm rate tracked.

### Q3 — P8 tester release

**Do:** Cohort **20–30** active BTC options traders. Ship P8 conclusion / learn loop. Write **validation report** (comprehension, confirm, return, paid interest). Unblock **VPS research beta URL**.

**Defer:** Paywall automation; live execution.

**Learn from:** Robinhood waitlist; Coinbase referrals; one anchor power user (Plaid / Venmo pattern).

**Checkpoint:** ≥5 “would pay something”; Sean Ellis **≥40%** “very disappointed if gone” in cohort.

### Q4 — Evidence-based fork

**Do:** P8 report drives **next SELECTION** — do not auto-widen.

| Validation says | Peer pattern | Action |
|-----------------|--------------|--------|
| Strong lab, weak MSOS | SpotGamma | Double down PPE; slow shell polish |
| Thesis → expression clicks | Composer (sim) | MSOS workflow + subscription |
| Embed demand | Plaid | Productize embed/API boundary |
| Wrong audience | PayPal pivots | Change **who**, not features |
| Weak everywhere | Quantopian lesson | One screen, one cohort; stop platform expansion |

---

## MSOS queue ↔ playbook

| Chapter | Playbook role | Rule |
|---------|---------------|------|
| **P6** (expression sim) | Q1 narrative completeness | **Sim-only** — no execution creep |
| **P7** (monitoring) | Q2 return hook | Ship **minimum** that drives weekly return |
| **P8** (tester release) | Q3 PMF gate | Validation report **bosses** next-year queue |
| **MVP1** (when SELECTION'd) | Q1–Q2 | Only if improves 15-second comprehension or disagreement |

---

## Drift guards (say no)

Stop and escalate if a BUILD packet would:

1. **Port PPE math to TypeScript** — hard rule ([`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md)).
2. **Add live execution or order routing** — deferred until P8 + new SELECTION.
3. **Expand assets** (gold, Polymarket arb, perps) — without validation report approval.
4. **Add AI assistant / auto trade recommendations** — [`PRODUCT_THESIS.md`](../PRODUCT_THESIS.md) out of scope.
5. **Build platform surface** without a tester pull signal — Command Center polish before return rate proven.
6. **Claim traction, TAM, edge, or profitability** without evidence — MSOS non-widening rule.

**Escalation:** Steward thread + update **Current stage** table after monthly review.

---

## Metrics (log in VALIDATION_REALITY_CHECKS)

| Metric | Target | When |
|--------|--------|------|
| Time-to-aha | New tester explains market-implied vs belief in **<15 min** | Every session |
| Return rate | **≥3/10** return in 7 days | End Q1 |
| WAU/MAU (cohort) | **≥40%** WAU | End Q2 |
| Thesis confirm | Track % reaching P5 confirm | Q2+ |
| Paid interest | **≥5** would-pay signals | End Q3 |
| PMF survey | **≥40%** “very disappointed if gone” | End Q3 |
| P8 validation report | Written; next SELECTION recorded | P8 closeout |

---

## Peer lessons (compact reference)

| Peer | Lesson for us |
|------|----------------|
| **Plaid** | Consumer app failed; **infrastructure wedge** won. Watch embed/API pull. |
| **PayPal** | Palm → email → **eBay**. Users pick the business. |
| **Robinhood** | One promise; **years** on compliance before scale. Sim-only is our shortcut. |
| **Coinbase** | Early BTC niche, Reddit/HN, hand-held first users. |
| **SpotGamma** | One chart, one audience, subscription. |
| **Quantopian** | Great UX without pay/return loop → failure. |
| **Facebook (early)** | One campus density before expansion = **friends-first cohort**. |

---

## 90-day action list (operator)

1. Recruit **10** active BTC options traders (not generic crypto friends).
2. Run **same session script** (below) every time.
3. Log every session in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
4. Finish **P6**; do not block sessions on P7.
5. Ship **one public research-beta URL** (VPS CTA).
6. **Month 3:** If return rate fails checkpoint, steward SELECTION = MVP1 legibility only.

---

## Session script (tester)

1. **Open** BTC implied lab — chart visible without scroll.
2. **Market-implied:** “What price range does the market lean toward by expiry?”
3. **User belief:** Adjust belief; switch compare mode.
4. **Disagreement:** Read disagreement strip — descriptive only, not a trade signal.
5. **Payoff fit:** Inspect structure stats (debit/credit, max loss, breakevens).
6. **Save:** Freeze snapshot or confirm thesis (P5 path when in MSOS).
7. **Close:** “Would you open this before your next options trade?” + log row.

Use [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) for timing detail.

---

## BUILD packet hook (optional)

When steward authorizes a slice that touches product scope, add to the packet:

```markdown
## Focus playbook
- Priority tier: P0 / P1 / P2 (from priority stack above)
- Drift guards checked: yes / N/A — <note if exception>
```

See [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md).

---

## Runtime layer (automation — thin)

Agents on **IDE BUILD** get a **3-line Focus block** in `IDE_BUILD_STARTER_*.md` only — not this full doc.

| Mechanism | Behavior |
|-----------|----------|
| `ppe_focus_gate.py` | Blocks auto-select / propagate while validation report is **DRAFT** or **MISSING** |
| `urgent: true` on backlog/queue row | Bypasses gate — requires `urgentReason` |
| `PPE_FOCUS_GATE=0` | Disable gate (escape hatch) |
| Active `RUNNING` manifest | Not cleared by gate — finish in-flight chapter first |

Full playbook loads: **steward SELECTION**, backlog edits, monthly review ([`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md)).

---

## Backlog and SELECTION (use this mythos)

1. Read [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md) + **Priority stack** + **Drift guards**.
2. Tag rows with `focusPlaybookTier` and `[P0]`–`[P4]` in `reason`.
3. After P8 cohort: complete validation report §6 before new **READY** queue rows (unless `urgent`).

| Playbook tier | Backlog `priority` hint |
|---------------|-------------------------|
| **P0** wedge proof | often `high` |
| **P1** chartered closeout | `high` / `medium` |
| **P2** lab legibility | `medium` |
| **P3** distribution | `medium` |
| **P4** monetization | `medium` after validation |
| **defer** | `low` or `blocked` without plan |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-12 | v1 — initial playbook from product/strategy working session |
| 2026-06-12 | Runtime gate + backlog mythos + operating calendar |
