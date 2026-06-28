# Forward Consistency Bybit v1

**Program:** [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md)  
**SELECTION:** [`POST_FORWARD_CONSISTENCY_BYBIT_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_BYBIT_V1_SELECTION.md)  
**Blocked until:** `forward_consistency_v1` **COMPLETE**

---

## Sprint intent

Extend forward consistency to **Bybit venue** (SOL first): option + linear future/perp bid/ask, same JSON contract and Strategy Lab panel behavior.

---

## Acceptance

1. `fetch_bybit_*` bid/ask wired into `forward_consistency_quotes.py`.
2. SOL enabled asset returns `comparable: true` when quotes exist.
3. Honest `BAD_DATA` / `WATCH` on thin books — no false `POSSIBLE_ARB`.
4. Tests with mocked Bybit tickers.
5. Evidence doc green.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| Product 002 | PRODUCT | PPE_CORE | Bybit quote adapter + engine integration |
| Closeout 004 | EVIDENCE | CONTROL | COMPLETE → surfaces SELECTION |

---

## Not now

- BNB/XRP until tier-1 enabled + witnessed
- Cross-venue Polymarket parity
