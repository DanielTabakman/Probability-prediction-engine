# MVP1 probability method legibility — relay sprint spec

**Controlling canon:** [`docs/SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md)  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md)  
**SELECTION:** [`POST_MVP1_PROBABILITY_METHOD_LEGIBILITY_SELECTION.md`](POST_MVP1_PROBABILITY_METHOD_LEGIBILITY_SELECTION.md)  
**Relay baseline:** **`main`**

---

## Sprint intent

Ship **method-labeled** UI copy so users can tell what each probability number on the implied lab chart and Polymarket comparison table represents, and how **belief → strategy families** are derived — without changing purple/orange/belief math, disagreement thresholds, or MSOS shell work.

---

## Sprint-level acceptance

1. **15-second legibility:** user can name purple vs orange vs teal curves and knows y-axis % is scaled density, not cumulative probability.
2. User can explain strategy families are **rule-based fit**, not optimized tickets.
3. Polymarket spread table columns state **method** explicitly.
4. Optional pointwise **P(> strike)** columns on aligned Polymarket rows (lognormal + options-integrated).
5. **`python -m pytest -q`** green; **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0**.
6. Evidence in [`MVP1_PROBABILITY_METHOD_LEGIBILITY_EVIDENCE_STATUS.md`](MVP1_PROBABILITY_METHOD_LEGIBILITY_EVIDENCE_STATUS.md).

---

## Not now

- Change lognormal, Breeden–Litzenberger, or belief classification math.
- Arb automation or “recommended trade” language.
- MSOS Strategy Lab shell / proxy work (MSOS P4 track).
- IV-surface method A upgrade (future chapter).

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MVP1-ProbMethodLegibility-Control-Slice001** | CONTROL | CONTROL | Charter + backlog row + frontier note |
| **MVP1-ProbMethodLegibility-Product-Slice002** | PRODUCT | PPE_UI | Chart legend, axis, cumulative caption, glossary |
| **MVP1-ProbMethodLegibility-Product-Slice003** | PRODUCT | PPE_UI | Belief → strategy “how calculated” surface |
| **MVP1-ProbMethodLegibility-Product-Slice004** | PRODUCT | PPE_UI | Polymarket table method labels |
| **MVP1-ProbMethodLegibility-Product-Slice005** | PRODUCT | PPE_UI + ppe-core | Pointwise P(> strike) comparison columns |
| **MVP1-ProbMethodLegibility-Smoke-Slice006** | CONTROL | CONTROL | pytest + dual smoke |
| **MVP1-ProbMethodLegibility-Closeout-Slice007** | CONTROL | CONTROL | Chapter closeout docs |

---

## Sprint status

**COMPLETE** — chartered + product legibility shipped on feature branch; backlog row remains **blocked** until MSOS P4 **COMPLETE** for relay auto-select.
