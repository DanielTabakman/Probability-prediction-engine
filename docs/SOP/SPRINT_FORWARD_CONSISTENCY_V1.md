# Forward Consistency v1 — core spine

**Program:** [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md)  
**SELECTION:** [`POST_FORWARD_CONSISTENCY_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_V1_SELECTION.md)  
**Baseline:** `main`  
**Pre-build note:** Substantial implementation on **PR #447** — BUILD verifies merge + witness.

---

## Sprint intent

Ship the **core spine**: parity engine, Deribit bid/ask quotes, JSON boundary, Streamlit debug spike, Strategy Lab **No-Arbitrage Check** panel for BTC/ETH.

---

## Acceptance

### A — Engine (Python)

1. Put-call parity synthetic forward from bid/ask only.
2. Status enum: `NO_ARB`, `WATCH`, `POSSIBLE_ARB`, `BAD_DATA`, `NOT_COMPARABLE`.
3. Unit tests: inside band, both arb directions, missing bids, crossed synth, rank tightest strike.

### B — API

1. `GET /forward-consistency.json?asset=&expiry=` on display API WSGI app.
2. Deribit BTC/ETH; Bybit/equity → `NOT_COMPARABLE` with honest copy.

### C — MSOS

1. `ForwardConsistencyPanel` on Strategy Lab (asset + expiry synced).
2. Sample-mode fixture when not live.
3. Copy: spot vs chart median vs arb frame.

### D — Witness

1. pytest engine + boundary + MSOS witness.
2. Evidence doc updated.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| Control 001 | EVIDENCE | CONTROL | Selection + evidence scaffold |
| Product 002 | PRODUCT | PPE_CORE + MSOS_UI | Engine, API, panel (PR #447) |
| Closeout 004 | EVIDENCE | CONTROL | Chapter COMPLETE → bybit SELECTION |

---

## Not now

- Bybit SOL, Horizon strip, archive, expression bridge, execution
