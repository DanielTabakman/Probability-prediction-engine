# PPE Deribit crypto tier-1 v1 — relay sprint spec

**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Prior chapter:** [`SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md`](SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md) (COMPLETE)  
**Manifest:** [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml)  
**SELECTION:** [`POST_PPE_DERIBIT_CRYPTO_TIER1_V1_SELECTION.md`](POST_PPE_DERIBIT_CRYPTO_TIER1_V1_SELECTION.md)

---

## Sprint intent

Enable **SOL, BNB, XRP** on Deribit via registry rows + witness — no new fetch fork.

**Assets:** `SOL`, `BNB`, `XRP` — verify Deribit instrument listing before `enabled: true`.

---

## Slice acceptance

| Slice | Plane | Deliverable |
|-------|-------|-------------|
| PPE-CryptoT1-Control-Slice001 | CONTROL | Charter witness |
| PPE-CryptoT1-Core-Slice002 | PPE_CORE | Merge manifest rows; per-asset witness + enable |
| PPE-CryptoT1-Witness-Slice003 | CONTROL | pytest + production spot-check |
| PPE-CryptoT1-Closeout-Slice004 | CONTROL | Evidence COMPLETE |

---

## Non-goals

- Fourth+ Deribit currencies without new SELECTION
- MSOS picker changes (catalog-driven from universe v1)
