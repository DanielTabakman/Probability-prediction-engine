# MSOS self-serve onboarding v1

**Controlling canon:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) workstream **A** · [`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md)  
**SELECTION:** [`POST_MSOS_SELF_SERVE_ONBOARDING_V1_SELECTION.md`](POST_MSOS_SELF_SERVE_ONBOARDING_V1_SELECTION.md)  
**Priority:** **P0** — trader workflow integration (self-serve onboarding)  
**Baseline:** **`main`**

---

## Sprint intent

Harden **self-serve onboarding**: public URL → guided Strategy Lab tour → disagreement loop entry **without operator narration**. Foundation exists (`platformTutorial.ts`, homepage CTA, nav restart); this chapter makes the contract **production-green** and **BTC + ETH aware** after crypto multi-asset closeout.

**Operator goal:** A cold visitor on production completes the tour and reaches thesis confirmation without a scheduled demo.

---

## Preconditions

1. `msos_usable_demo_v1` **COMPLETE** — walkable shell + PPE embed
2. `ppe_crypto_multi_asset_v1` **COMPLETE** — BTC + ETH selector in Strategy Lab
3. Public demo launch **COMPLETE** — apex URL live

---

## Acceptance

### A — Tutorial UX

1. First visit auto-opens tour unless `localStorage` completion flag set.
2. `?tutorial=1` and `?tutorial=beginner` force appropriate step sets.
3. Tour copy references **asset-agnostic** crypto wording (BTC default; ETH switcher discoverable).
4. All `data-tour` anchors resolve on live Strategy Lab layout (no dead spotlight targets).
5. **Restart tour** in public nav clears flag and re-opens tour.

### B — Self-serve entry points

1. Homepage hero + features CTA route to tour entry (`strategyLabTutorialHref` or equivalent).
2. Honest demo/live labels preserved — no fake “signed in” chrome.

### C — Witness

1. pytest tutorial wiring tests green.
2. Evidence doc operator checkboxes signed at closeout.
3. Tutorial contract documented in [`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md).

---

## Relay slices (summary)

| Slice | Plane | Intent |
|-------|-------|--------|
| `MSOS-SelfServeV1-Control-Slice001` | EVIDENCE | Charter + direction align |
| `MSOS-SelfServeV1-Product-Slice002` | PRODUCT | Tutorial steps, anchors, ETH-aware copy |
| `MSOS-SelfServeV1-Product-Slice003` | PRODUCT | Homepage/nav CTAs + first-run polish |
| `MSOS-SelfServeV1-Witness-Slice004` | EVIDENCE | pytest + evidence witness |
| `MSOS-SelfServeV1-Closeout-Slice005` | EVIDENCE | Chapter COMPLETE + steering sync |

---

## Carry docs

- [`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md)
- [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md)
- [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json)
