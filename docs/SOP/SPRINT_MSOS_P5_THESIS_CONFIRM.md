# MSOS P5 — thesis confirmation + durable state

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P5)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md) — screen `04_confirmation`  
**Semantics:** [`MSOS_Product_Semantics_State_Model_v0.1.md`](../VISION/MSOS/storyboard-v0.6/semantics/MSOS_Product_Semantics_State_Model_v0.1.md)  
**Acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) — fixture-first UI, then persistence  
**SELECTION:** [`POST_MSOS_P5_THESIS_CONFIRM_SELECTION.md`](POST_MSOS_P5_THESIS_CONFIRM_SELECTION.md)

---

## Sprint intent (P5)

Ship thesis confirmation UI (Exploring → Draft → Confirmed) aligned to `04_confirmation`. **Phase A:** fixture/mock state in Next.js. **Phase B (same chapter if scoped):** minimal persistence for save/reopen — no live execution CTA.

## Preconditions (at SELECTION)

1. P4 Strategy Lab / PPE integration **COMPLETE**.
2. P2/P3 shell and tokens reusable.

## Acceptance

1. Confirmation route matches storyboard narrative (“Is this what you think is true?”).
2. CTA is **Proceed to expression planning** — not execute.
3. Honest labels for reference/trust context; no hidden authority.
4. Screenshot witness vs `prototype/screens/04_confirmation.png`.
5. Persistence witness documented in evidence (API shape or local store — no false Live claims).

## Not now

- Live execution (P6 sim-only first).
- Hyperliquid beyond Pending.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-P5-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align |
| **MSOS-P5-Product-Slice002** | PRODUCT | MSOS_UI | Confirmation UI + persistence boundary |
| **MSOS-P5-Witness-Slice004** | EVIDENCE | CONTROL | pytest + visual witness |
| **MSOS-P5-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close |
