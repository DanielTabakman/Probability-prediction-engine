# MSOS usable demo v1

**Controlling canon:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) · [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md)  
**Visual reference:** storyboard v0.6 — [`docs/VISION/MSOS/storyboard-v0.6/prototype/html/`](../VISION/MSOS/storyboard-v0.6/prototype/html/)  
**SELECTION:** [`POST_MSOS_USABLE_DEMO_V1_SELECTION.md`](POST_MSOS_USABLE_DEMO_V1_SELECTION.md)  
**Priority:** **P0** — usable demo BUILD (post storyboard design)  
**Baseline:** **`main`**

---

## Sprint intent

**Storyboard design is complete.** This chapter **BUILDs** the walkable product: MSOS shell routes per storyboard with **PPE integrated inside** Strategy Lab — not a friends-first research gate, not a fixture tour.

**Operator goal:** A visitor on production MSOS URLs walks the storyboard journey (home → command center → strategy lab with live PPE chart region → thesis → expression → monitor/history) as **one cohesive demo**.

**Non-goals:** Friends-and-family cohort gating; trader workflow research as BUILD blocker; new asset classes; live execution.

---

## Preconditions

1. Storyboard v0.6 HTML/CSS prototypes in-repo — **met**
2. MSOS web routes exist for storyboard screens — **partial** (shell routes shipped; integration hardening remains)
3. PPE math stays in Python — **binding** ([`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md))

---

## Acceptance

### A — Strategy Lab + PPE integration

1. `/strategy-lab` chart region shows PPE distribution per storyboard `03_ppe_lab` hierarchy — display API or honest chromeless embed; **no box-in-box full Streamlit chrome** as default.
2. Belief builder + outcome panel remain MSOS-native.
3. Honest Live/degraded labels when PPE upstream unavailable.

### B — Demo walkability

1. Operator can walk storyboard route chain on production URLs without a 20-minute explanation ([`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)).
2. Save/review/history visible in UX (server-side preferred; honest preview labels acceptable).
3. Witness checkboxes in evidence doc signed at closeout.

### C — Platform + witness

1. Deploy docs current ([`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md)).
2. pytest + visual witness for Strategy Lab integration path.

---

## Relay slices (summary)

| Slice | Plane | Intent |
|-------|-------|--------|
| `MSOS-UsableDemoV1-Control-Slice001` | EVIDENCE | Charter + direction align |
| `MSOS-UsableDemoV1-Product-Slice002` | PRODUCT | PPE display boundary + embed shell hardening |
| `MSOS-UsableDemoV1-Product-Slice003` | PRODUCT | MSOS chart shell + storyboard layout on `/strategy-lab` |
| `MSOS-UsableDemoV1-Witness-Slice004` | EVIDENCE | pytest + operator demo witness |
| `MSOS-UsableDemoV1-Closeout-Slice005` | EVIDENCE | Chapter COMPLETE + steering sync |

---

## Carry docs

- [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md)
- [`MSOS_PRODUCTION_LIVE_HOOKUP_V1.md`](MSOS_PRODUCTION_LIVE_HOOKUP_V1.md)
- [`PRODUCT_DIRECTION_PIVOT_V1.md`](PRODUCT_DIRECTION_PIVOT_V1.md)
