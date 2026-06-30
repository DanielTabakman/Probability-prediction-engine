# Founder-operator crib sheet v1

**For:** human operator (you) — guided demos and outreach, not agents.  
**Strategic context:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) § Founder-operator  
**Timed walkthrough:** [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) · **Session log:** [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md)

---

## Phone cue card (panic in the room)

**Session notebook (recommended):** step-by-step walkthrough that advances as you go — [`OPERATOR_SESSION_NOTEBOOK_V1.md`](OPERATOR_SESSION_NOTEBOOK_V1.md)

| How | URL |
|-----|-----|
| **Live** | `https://marketstructureos.com/session.html` |
| **Offline** | [`assets/operator_session_notebook.html`](assets/operator_session_notebook.html) + `session.json` in same folder |

Add to **Home Screen** on your phone. Glance under the table — traders see the demo, not your notebook.

**Static panic sheet (legacy):** [`assets/operator_cue_card.html`](assets/operator_cue_card.html) — redirects to session notebook when deployed.

**Do not** share these links with testers.

---

## Wrong doc? (agents + humans)

```bash
python scripts/resolve_sop.py --topic "<what you're working on>" --json
python scripts/resolve_sop.py --list-topics
```

Index: [`CHAPTER_DOC_INDEX.json`](CHAPTER_DOC_INDEX.json) · canon: [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)

---

## North star (say every session)

> See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds.

You explain **meaning**, not derivations.

---

## Five concepts (no equations)

| Concept | One sentence |
|---------|----------------|
| **Market-implied curve** | Given today’s option prices, this is the **shape the market has priced in** for this expiry — a readout, not a forecast. |
| **Your belief** | If you think differently (higher, wider, etc.), you overlay **your** view on the same chart. |
| **Disagreement** | The strip names **where** your view and the market’s priced view **differ** — descriptive, not buy/sell. |
| **Strategy families** | **Shapes that fit** the disagreement story — exploratory, not “do this trade.” |
| **Green payoff line** | An **exact structure** from this run’s strikes and prices — different from illustrative families. |

Canon: [`SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md)

---

## 3-minute demo path

1. **Intro (30s)** — “BTC options research cockpit — not advice.”
2. **Chart (60s)** — “Purple/orange = what the market prices in at this expiry.”
3. **Belief preset (60s)** — Click one preset; “If I think differently, I say so here.”
4. **Disagreement (60s)** — “Belief vs market — where we disagree, in plain language.”
5. **Close (30s)** — “Full app freezes what you saw for later review.”

**Skip unless they ask:** Polymarket, forward curve, Verification deep-dive, MSOS shell, ticket copy.

---

## When they ask “how is that calculated?”

| Who | Response |
|-----|----------|
| **Trader** | “Orange curve comes from the live options chain; purple is a simpler baseline. Open **Verification** / trust strip for provenance — that’s the audit trail.” |
| **Non-trader friend** | “Live Deribit quotes turned into a probability-shaped chart. I’m testing whether **options traders** find the workflow useful.” |

Do not improvise formulas on a call.

---

## Session questions (log immediately after)

1. **Comprehension:** “What was the main thing on screen — in your words?” → Pass = chart / implied / disagreement.
2. **Return:** “Would you open this before your next BTC options trade?” Y/N
3. **Paid interest** (session 4+ only): willingness to pay for beta/brief/call this quarter.

---

## Who counts toward 10 sessions

| Counts | Does not count |
|--------|----------------|
| Guided screen share with **options-aware** profile (BTC vol, Deribit, equity opts) | Generic “crypto friend” saying “cool” |
| Logged in § **MSOS P8 friends-first tester metrics** | Optional §15F spot-check only |

---

## Outreach text (copy/edit)

**Async (solo-default):** see [`OPERATOR_ASYNC_VALIDATION_V1.md`](OPERATOR_ASYNC_VALIDATION_V1.md).

**Live screen share (when scheduled):**

```text
Hey [Name] — I'm building a BTC options research demo (market-implied vs your view, ~5 min walkthrough). Not a trade signal — just structure legibility. Would you have 20 min this week for a guided look? Honest feedback from someone who trades options, not a pitch. https://marketstructureos.com
```
