# MSOS public copy v1 (trader-facing UI)

**Plane:** PRODUCT-PLANE · **Layer:** `msos-shell` · **Audience:** new BTC options traders on `marketstructureos.com`

**Canon:** [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md) · [`SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md) · [`OPERATOR_UX_WITNESS_V1.md`](OPERATOR_UX_WITNESS_V1.md)

---

## Why this doc exists

Internal copy (slice IDs, PPE jargon, fixture labels, steward notes) is useful **for operators and agents**. It is **wrong on the public site** — it reads like build notes, not a product.

**Rule:** Every string a visitor can see must sound like something a patient options trader would understand in one pass. When in doubt, read it aloud to someone who has traded options but never heard of MSOS.

---

## Audience

| Reader | What they need |
|--------|----------------|
| **New BTC options trader** | Plain language, no acronyms without explanation, no “we’re still building this” unless honest and short |
| **Operator (you)** | Internal docs, session notebook, SOP paths — **not** apex UI copy |
| **Agents** | This doc + `publicCopy.ts` helpers; machine witnesses catch breaks, not tone |

---

## Voice (do)

- **Short sentences.** One idea per line in panels.
- **Trader verbs:** read the market, state your view, plan a trade, paper trade, review, compare.
- **Honest limits:** “Paper only”, “Demo data”, “Coming soon” — never fake live.
- **Disagreement is descriptive:** “You think X; options imply Y” — not buy/sell, not “AI recommends”.
- **Second person:** “You think…”, “Your view…”, “Pick a preset…”
- **Name the market:** Deribit, BTC options, expiry, range, vol — words traders already use.

---

## Voice (don’t)

### Banned on public UI

| Internal / agent | Use instead |
|------------------|-------------|
| PPE, MSOS workflow store, display payload, embed, chromeless | options data, your workspace, chart, live quotes |
| Fixture, storyboard, slice, Screen 04, P8 | demo, preview, (omit) |
| Snapshot feed degraded, `bindings`, stack traces | Saved history isn’t connected yet — Strategy Lab still works |
| Frozen evaluation, implied-lab freeze | saved market read, captured view |
| Expression families, optimization basis, eligible rails | structure types, why this trade, where to trade |
| Materiality, classification trace, steward | gap, difference, review |
| VALIDATION_REALITY_CHECKS, SELECTION | (omit — operator-only) |

### Never

- Paste **error messages**, env var names, or module paths into UI.
- Present **fixture/demo** data without a visible “Demo” or “Preview” label when live data exists on the same page.
- Use **ALL CAPS section headers** like internal storyboard wireframes (`MARKET SURFACE COMPARISON`).
- Imply **guaranteed profit** or “recommended trade” voice.

---

## Where copy lives (code)

| Location | Use for |
|----------|---------|
| [`apps/msos-web/src/data/*Fixtures.ts`](../../apps/msos-web/src/data/) | Fallback/demo strings when live feeds empty |
| [`apps/msos-web/src/lib/publicCopy.ts`](../../apps/msos-web/src/lib/publicCopy.ts) | Shared footers, degraded messages, workspace labels |
| [`apps/msos-web/src/lib/beliefPresets.ts`](../../apps/msos-web/src/lib/beliefPresets.ts) | Belief preset labels + outcome sentences |
| [`apps/msos-web/src/lib/ppeDisplayPayload.ts`](../../apps/msos-web/src/lib/ppeDisplayPayload.ts) | Live metrics/outcome copy from display API |
| [`apps/msos-web/src/lib/monitorHistoryFeed.ts`](../../apps/msos-web/src/lib/monitorHistoryFeed.ts) | Dynamic monitor/history strings |
| [`apps/msos-web/src/components/*.tsx`](../../apps/msos-web/src/components/) | Page chrome, headings, empty states — **minimize** inline copy; prefer data/lib |
| Page `metadata` in `apps/msos-web/src/app/**/page.tsx` | Browser tab + SEO one-liners |

**Prefer:** add reusable strings to `publicCopy.ts` or fixtures — avoid scattering one-off jargon in components.

---

## Copy checklist (every `msos-shell` UI slice)

Before marking IDE BUILD ready:

1. [ ] Read every new/changed string aloud — would a new trader get it?
2. [ ] No banned terms in visitor-visible text (grep: `PPE`, `fixture`, `workflow store`, `embed`, `snapshot feed`, `Screen 0`, `VALIDATION`).
3. [ ] Degraded/error paths use [`friendlySnapshotFeedMessage`](../../apps/msos-web/src/lib/publicCopy.ts) or equivalent — no raw exceptions.
4. [ ] Footer uses `DEMO_FOOTER` or matches its intent (paper trading, no live orders).
5. [ ] Live vs demo is obvious (pill, tag, or metric label).
6. [ ] Witness tests updated if they asserted **old internal strings** — tests should assert structure/wiring, not freeze bad copy.

### Homepage canon (2026-06)

| Element | Copy |
|---------|------|
| Primary CTA | Explore the platform |
| Hero pills | Your thesis stays yours · Expression, not recommendation · BTC options live preview |
| Product cards | Market Structure OS · Strategy Lab · **Probability Engine** (not “PPE” on homepage) |
| Command Center preview | Thesis gap (not “Disagreement located” on homepage) |

---

## Examples (before → after)
|--------|-------|
| Live via PPE · distribution math stays in Python | From Deribit options — updated with market quotes |
| MSOS workflow store | Saved to your workspace |
| Snapshot feed degraded: Cannot find module 'bindings' | Saved history isn’t connected yet. Strategy Lab still works. |
| Market-implied vs reference vs your belief (Lognormal benchmark PPE) | Market vs your view — purple curve = what options imply today |
| Confirm thesis → Proceed to expression planning | Confirm view → Plan a paper trade |
| Research demo — KPIs from PPE snapshots (read-only) | Research preview — paper trading only. Nothing here sends a live order. |

---

## Human vs machine (UX witness)

| Machine (CI) | Human (operator solo) | Visitors (async) |
|--------------|----------------------|------------------|
| HTTP + Playwright + `msos_public_copy_gate.cmd` | 3-checkbox pass — [`OPERATOR_UX_WITNESS_V1.md`](OPERATOR_UX_WITNESS_V1.md) | `/feedback` + Strategy Lab strip |
| Banned jargon FAIL; fixture strings WARN | Tone, link-ready | Export via `ppe_export_web_feedback.py` |
| Playwright scans rendered HTML | Optional reality-check row | Operator inbox `/operator/feedback` |

See [`OPERATOR_ASYNC_VALIDATION_V1.md`](OPERATOR_ASYNC_VALIDATION_V1.md).

---

## Internal copy is still fine elsewhere

- `docs/SOP/*`, phase plans, IDE_BUILD_STARTER, operator session notebook — **keep** internal precision.
- Streamlit / PPE lab — operator-facing tool; different audience.
- Code comments and variable names — no need to dumb down.

Only **`apps/msos-web/` visitor surfaces** and **production metadata** follow this doc.

---

## When to revise this doc

- Operator feedback: “this still sounds like notes” → add banned term or example row, then fix UI in same pass.
- New surface (billing, social, email) → add audience row and checklist item before BUILD charters it.

**History:** Trader copy pass landed 2026-06-22 (`copy(msos-shell): rewrite public UI for new options traders`).
