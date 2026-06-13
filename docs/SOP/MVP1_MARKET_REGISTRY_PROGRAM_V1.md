# MVP1 market registry program v1

**Purpose:** Config-driven onboarding for new tradable markets (Deribit crypto first, equities later) without forking the implied lab per asset.

**As-of:** 2026-06-13 · **Controlling playbook:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)

**North star (program):** Add a new Deribit market with **YAML + smoke** — no `app.py` surgery.

**Product north star (unchanged):** BTC options implied lab remains default surface until validation authorizes widening.

---

## Chapter sequence (relay order)

| # | Chapter | Priority | Blocked until | Delivers |
|---|---------|----------|---------------|----------|
| 1 | `mvp1_market_registry_core_v1` | MEDIUM · 4 | cross-venue scan COMPLETE (or steward override) | `config/markets.yaml`, `MarketRegistry`, generic Deribit provider |
| 2 | `mvp1_market_registry_lab_ui_v1` | MEDIUM · 5 | core COMPLETE | `market_session.py`, parameterized cache + UI; BTC parity |
| 3 | `mvp1_market_registry_crypto_activate_v1` | MEDIUM · 6 | lab UI COMPLETE | ETH + SOL enabled in config; smoke + honest liquidity banners |
| 4 | `mvp1_market_registry_equity_provider_v1` | LOW · 7 | crypto activate COMPLETE + equity pull signal | Yahoo equity provider (NVDA pilot); disabled by default |

Mechanical order: **high → medium → low**; within medium, **backlog file order** (slots 4–6 above). Does **not** supersede MSOS visual parity, public demo, or cross-venue prob panel / scan (slots 1–3).

---

## Architecture (target)

```text
config/markets.yaml  →  MarketRegistry  →  Provider (deribit | yahoo_equity)
                              ↓
                    Normalized MarketQuotes (spot, forward, marks, expiries)
                              ↓
                    src/viz/market_session.py  →  implied lab (unchanged math)
```

**Normalized contract:** `mark_native` (underlying-denominated premium) × forward → USD; replaces hardcoded `mark_btc` and `price_min = 1000`.

**Drift guards:** No TS math port; no execution; no “all assets supported” marketing until smoke + guided session logged in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

---

## Slice map (within chapters)

### Chapter 1 — core (`mvp1_market_registry_core_v1`)

| Slice | Layer | Work |
|-------|-------|------|
| 1 | ppe-core | `MarketProfile` + `MarketRegistry.load()` + tests |
| 2 | ppe-core | Parameterize `fetch_deribit` by currency; `mark_native`; keep BTC wrappers |

### Chapter 2 — lab UI (`mvp1_market_registry_lab_ui_v1`)

| Slice | Layer | Work |
|-------|-------|------|
| 3 | ppe-ui | `market_session.py` + asset-scoped cache keys |
| 4 | ppe-ui | Parameterize `app.py` / panels / export; asset selector (BTC only enabled initially) |

### Chapter 3 — crypto activate (`mvp1_market_registry_crypto_activate_v1`)

| Slice | Layer | Work |
|-------|-------|------|
| 5 | config + smoke | Enable ETH in `markets.yaml`; smoke + session log |
| 6 | config + smoke | Enable SOL; min-strike / quote-density banner |

### Chapter 4 — equity provider (`mvp1_market_registry_equity_provider_v1`)

| Slice | Layer | Work |
|-------|-------|------|
| 7 | ppe-core | `YahooEquityProvider` → same `MarketQuotes`; NVDA disabled until charter |

---

## Onboarding checklist (after chapter 3)

```text
□ Deribit lists options on {CURRENCY}?  (get_instruments)
□ Add block to config/markets.yaml
□ Set enabled: true + ui.price_floor / price_step
□ python scripts/smoke_market.py --asset {id}   (add script in chapter 3)
□ One guided session → VALIDATION_REALITY_CHECKS.md
```

---

## What each phase excludes

| Phase | Not now |
|-------|---------|
| core | UI asset picker, ETH/SOL enabled, equities |
| lab UI | New enabled assets; MSOS shell picker |
| crypto activate | On-chain Solana; wallet connect |
| equity provider | Dividend-adjusted American options; auto-trade |

---

## Commercial framing

- **Deribit ETH/SOL:** CeFi vol — good for crypto Spaces contacts; not on-chain DeFi.
- **Equities:** Manual brief first ([`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) Q-007); provider slice only when pull exists.

---

## Related

- [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md)
- [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) — runs at medium slots 2–3 before this program
- [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md)
