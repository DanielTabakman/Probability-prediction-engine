# Asset data source discovery v1

**Purpose:** Agents discover **where each asset's market data comes from** and whether that source is **live** — without asking the operator. Required before enablement, tier-1 batch BUILD, or answering "where does X data come from?"

**As-of:** 2026-06-27 · **Related:** [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md) · [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md)

---

## SSOT order

| Question | Read first |
|----------|------------|
| Per-asset routing (`venue`, symbols) | [`config/assets.yaml`](../../config/assets.yaml) |
| Venue → fetch module + probe hints | [`config/asset_venue_source_map.yaml`](../../config/asset_venue_source_map.yaml) |
| Live availability right now | `python scripts/probe_asset_data_source.py --asset <ID> --json` |
| Enable ritual | [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md) |

---

## Where data comes from today (PPE)

| `venue` | Fetch module | Vendor | Used for |
|---------|--------------|--------|----------|
| `deribit` | `src/data/fetch_deribit.py` | [Deribit public API](https://www.deribit.com/api/v2) | Crypto **options** implied lab (BTC, ETH, …) |
| `equity` | `src/data/fetch_equity_options.py` | Yahoo Finance (`yfinance`) | US equity + ETF **options** (NVDA, SPY, GLD, …) |

MSOS **never** fetches vendors directly — it reads PPE `catalog.json` + `display.json` only.

**Deferred (not wired):** `venue: cme` — see [`POST_PPE_CME_COMMODITY_V1_SELECTION.md`](POST_PPE_CME_COMMODITY_V1_SELECTION.md).

---

## SOL specifically (2026-06-27)

| Layer | Source | Status |
|-------|--------|--------|
| **Registry** | `config/assets.yaml` → `venue: deribit`, `deribit_currency: SOL` | Row exists, `enabled: false` |
| **Implied options chain** | `fetch_deribit.py` → `get_instruments(currency=SOL, kind=option)` | **0 instruments** — delisted on Deribit |
| **Spot / index only** | Deribit `sol_usd` index, `SOL_USDC` spot | Live — **not enough** for Strategy Lab (needs options) |
| **Alternatives** | OKX, Bybit, etc. | **Not implemented** — requires new `venue` adapter + SELECTION |

Run: `python scripts/probe_asset_data_source.py --asset SOL`

---

## Agent ritual (mandatory — do not ask operator first)

### Triggers

- Operator asks about an asset's data source or "can we enable X?"
- Before `enabled: true` on any registry row
- Before tier-1 batch relay Core slice (merge manifest → `assets.yaml`)
- Witness failure / empty chain on a newly enabled asset
- Chapter evidence for crypto tier1, equity tier1, commodity proxy

### Steps

1. **Read registry row** — `config/assets.yaml` → `venue`, `deribit_currency` / `equity_symbol` / `data_source`.
2. **Read venue map** — `config/asset_venue_source_map.yaml` for probe rules + research alternatives.
3. **Run probe** (live network OK on steward desktop):

   ```bash
   python scripts/probe_asset_data_source.py --asset SOL --json
   python scripts/probe_asset_data_source.py --manifest-slice ppe_deribit_crypto_tier1_v1 --json
   ```

4. **Decide:**

   | Probe result | Action |
   |--------------|--------|
   | `options_available: true` | Proceed to witness + enable pipeline |
   | `options_available: false`, primary venue | **Block enable** — document skip in chapter evidence; update `trust_notes` |
   | Primary dead, alternatives in map | File research note in evidence; **do not** silently switch venue — new SELECTION + adapter chapter |

5. **Record** probe JSON snippet or summary table in chapter `*_EVIDENCE_STATUS.md` (date + instrument counts).

### Do not

- Assume Deribit lists all tier-1 cryptos because BTC/ETH work
- Enable from manifest defaults without live probe
- Add a new vendor fetch fork inside a tier-1 **content** chapter (meta infra: new `venue` = new ADR + SELECTION)

---

## Adding a new venue (when primary fails)

Example: SOL options move to OKX.

1. **SELECTION** — new chapter (e.g. `ppe_okx_crypto_options_v1`) with vendor budget/API notes
2. **ADR** — extend [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md) venue table
3. **Fetch adapter** — `src/data/fetch_okx.py` → Deribit-shaped normalization (same engine contract)
4. **Registry** — `venue: okx` on SOL row (or split asset id if needed)
5. **Probe** — extend `scripts/probe_asset_data_source.py` + `asset_venue_source_map.yaml`
6. **Witness** — `witness_asset_catalog.py --asset SOL --live`

---

## Operator one-liner

```bash
python scripts/probe_asset_data_source.py --asset SOL
python scripts/probe_asset_data_source.py --asset NVDA --json
```

---

## Propagation

Agents: load this doc from [`agent-continuity.mdc`](../../.cursor/rules/agent-continuity.mdc) before asset enablement questions.

Update [`asset_venue_source_map.yaml`](../../config/asset_venue_source_map.yaml) when:

- A vendor delists or relists an asset
- A new venue adapter ships
- Research identifies a credible alternative for a blocked asset
