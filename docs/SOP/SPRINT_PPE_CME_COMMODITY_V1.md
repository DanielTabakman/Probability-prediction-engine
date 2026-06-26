# PPE CME commodity v1 — relay sprint spec

**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_CME_COMMODITY_V1_SELECTION.md`](POST_PPE_CME_COMMODITY_V1_SELECTION.md)  
**Status:** **DEFERRED** — charter only; BUILD blocked on validation pull.

---

## Sprint intent (when un-deferred)

Ship **GC, SI, CL** CME options through a new `venue: cme` fetch adapter with futures contract multiplier semantics and honest roll/expiry labeling.

---

## Planned slices (not READY)

| Slice | Deliverable |
|-------|-------------|
| PPE-CME-Control-Slice001 | ADR + vendor selection |
| PPE-CME-Core-Slice002 | `fetch_cme_options.py` + normalization |
| PPE-CME-UI-Slice003 | Streamlit + catalog |
| PPE-CME-Witness-Slice004 | Witness + evidence |

---

## Non-goals

- BUILD until gates in SELECTION doc pass
