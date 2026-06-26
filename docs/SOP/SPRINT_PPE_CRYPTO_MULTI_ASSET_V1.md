# PPE crypto multi-asset v1 — relay sprint spec

**Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05  
**Prior chapter:** [`SPRINT_MSOS_USABLE_DEMO_V1.md`](SPRINT_MSOS_USABLE_DEMO_V1.md) (must be COMPLETE)  
**SELECTION:** [`POST_PPE_CRYPTO_MULTI_ASSET_V1_SELECTION.md`](POST_PPE_CRYPTO_MULTI_ASSET_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Add **one additional crypto asset (ETH)** on **Deribit** using the same implied-distribution workflow as BTC. Introduce a small **asset registry** and thread `asset_id` through fetch → viz → embed boundary → MSOS display. **No math in TypeScript.**

**Priority:** MEDIUM — post usable-demo; pre equity expansion.

---

## Asset registry (v1)

File: `config/assets.yaml`

```yaml
version: 1
default_asset_id: BTC
assets:
  BTC:
    label: "BTC options"
    venue: deribit
    deribit_currency: BTC
    price_unit: USD
    spread_width: 5000
    trust_notes: []
  ETH:
    label: "ETH options"
    venue: deribit
    deribit_currency: ETH
    price_unit: USD
    spread_width: 500
    trust_notes:
      - "Thinner books than BTC — BL curve may be noisier; surface trust state in lab."
```

---

## Technical constraints (binding)

| Rule | Detail |
|------|--------|
| Layer | Math/fetch in `ppe-core`; lab in `ppe-ui`; shell in `msos-shell` |
| No TS math | MSOS reads `display.json` only |
| Cache keys | Every `@st.cache_data` wrapper that touches options data must include `asset_id` |
| Backward compat | Missing `asset` in API requests defaults to `BTC` |
| Spread defaults | Asset-specific `spread_width` in registry — not hardcoded in fetcher |
| Payload | Add optional `asset` block to `distribution_display_boundary` schema v1 (non-breaking) |

---

## Slice acceptance

### PPE-CryptoMA-Control-Slice001 (CONTROL)

- SELECTION record finalized; evidence stub; `config/assets.yaml` scaffold
- No product behavior change

### PPE-CryptoMA-Core-Slice002 (PPE_CORE)

- `fetch_deribit.py`: `currency` parameter; thin wrappers or aliases for existing BTC call sites during migration
- `distribution_export.py`: `asset_id` from registry, not hardcoded `"BTC"`
- Tests: parameterized fetch mocks; BTC regression

### PPE-CryptoMA-UI-Slice003 (PPE_UI)

- `app_cache.py`: asset-keyed caches; Streamlit asset selector
- `embed_display_boundary.py`: `asset` in payload
- `strategy_suggestion_boundary.py`: dynamic instrument labels
- Implied lab smoke passes for BTC + ETH

### PPE-CryptoMA-Product-Slice004 (MSOS_UI)

- Strategy Lab asset switcher (`?asset=ETH` or UI control)
- Copy from payload metadata (`buildThesisLabContext`, chart axis labels)
- `commandCenterFixtures`: ETH status → Live when wired
- MSOS tests updated

### PPE-CryptoMA-Platform-Slice005 (PLATFORM)

- Deploy/proxy: `display.json` asset query param if needed
- `msos_production_demo_witness.py`: ETH path or asset param
- Caddy/docker only if routing change required

### PPE-CryptoMA-Witness-Slice006 (CONTROL)

- `tests/test_implied_lab_embed_display_boundary.py`: asset field
- `tests/test_msos_web_strategy_lab.py`: ETH labels
- Operator witness checklist in evidence doc

### PPE-CryptoMA-Closeout-Slice007 (CONTROL)

- Evidence doc COMPLETE; frontier steer note; stocks chapter remains `blocked`

---

## Non-goals (repeat)

Equities, third crypto, Polymarket, execution, entitlements per asset.

---

## Sprint status

**CHARTERED** — blocked until `msos_usable_demo_v1` **COMPLETE**.
