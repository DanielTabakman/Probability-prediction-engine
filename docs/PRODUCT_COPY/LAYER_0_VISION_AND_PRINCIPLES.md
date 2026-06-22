# Layer 0 — Vision & principles (MSOS copy)

**Always load first** in a copy session. Stable context — edit when product direction pivots, not per string tweak.

**SSOT links:** [`ACTIVE_PRODUCT_DIRECTION.json`](../SOP/ACTIVE_PRODUCT_DIRECTION.json) · [`MSOS_PUBLIC_COPY_V1.md`](../SOP/MSOS_PUBLIC_COPY_V1.md) · [`LAYER_0_CONVERSION_FRAMEWORK.md`](LAYER_0_CONVERSION_FRAMEWORK.md) · [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md)

---

## Copy goal (visitor decision)

Good copy answers: **Is this for me? Do I understand the value? Do I trust it enough to take the next step?** — not “what is the product internally.”

Full funnel + homepage skeleton: **[`LAYER_0_CONVERSION_FRAMEWORK.md`](LAYER_0_CONVERSION_FRAMEWORK.md)** (load when drafting or revising strings).

---

## North star (15-second test)

> See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds.

---

## Job to be done (read before any surface edit)

> I have a market view. What does the options market imply? Where do I disagree? Is there a structure that fits my thesis?

---

## Platform promise (one paragraph)

Market Structure OS helps traders compare their thesis with what the market already implies, locate meaningful disagreement, and explore possible trade expressions — without hiding assumptions and without pretending to recommend trades.

---

## Product hierarchy (never invert in copy)

| Name | What it is | Copy rule |
|------|------------|-----------|
| **Market Structure OS** | Company + platform | Top-level brand on homepage and nav |
| **Command Center** | Authenticated home — ongoing work | Hub language: “pick up where you left off”, KPIs, tiles |
| **Strategy Lab** | Workspace for thesis + expression | Where the live BTC options demo lives today |
| **Probability Engine** | First tool inside Strategy Lab (PPE under the hood) | Say **Probability Engine** on public site — never “PPE” |
| **BTC options** | First enabled market lens | Live now; not permanent product identity |

---

## Interaction mode (current wedge)

**Disagreement mode** — compare market-implied probabilities with the trader’s view. Descriptive, not prescriptive. Other modes (hedging, monitoring, learning) are **Planned** — do not write copy that implies they ship today.

---

## Voice principles (do)

- Short sentences; one idea per panel line
- Trader verbs: read the market, state your view, plan a paper trade, review, compare
- Second person: “You think…”, “Your view…”
- Honest limits: Demo, Preview, Paper only, Coming soon, Planned — never fake live
- Name real markets: Deribit, BTC options, expiry, range, vol
- Disagreement is descriptive: “You think X; options imply Y”

---

## Voice principles (don’t)

- No buy/sell, no “AI recommends”, no guaranteed profit
- No internal build vocabulary: fixture, storyboard, slice, embed, workflow store, snapshot feed, PPE (public UI)
- No raw errors, env vars, or module paths in visitor text
- No ALL CAPS wireframe headers
- Do not over-promise: belief presets update text but chart overlay may lag; snapshot DB may degrade in Docker

---

## Compliance anchors (repeat across surfaces)

| Phrase | Use when |
|--------|----------|
| Expression, not recommendation | Homepage pill; anywhere structure is discussed |
| Your thesis stays yours | Privacy / ownership of belief |
| Paper trading only / Research preview | Footers, Command Center, monitor |
| Live demo / Live | Only when Deribit feed or honest live tag applies |

---

## Audience

**Primary:** New BTC options trader with a market view — traded options before, never heard of MSOS.

**Not the audience on public site:** Operators, stewards, agents — internal precision stays in `docs/SOP/`.

---

## When Layer 0 changes

- `ACTIVE_PRODUCT_DIRECTION.json` pivot (`pivotId` bump)
- Operator rewrites north star or platform promise
- New compliance requirement

**Next layer:** [`LAYER_1_PAGE_CATALOG.md`](LAYER_1_PAGE_CATALOG.md) — what each page is for and what’s on it.
