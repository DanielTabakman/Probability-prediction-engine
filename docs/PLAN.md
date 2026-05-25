# Probability Engine — Stack, Data Sources & Canonical Events

## Stack

| Layer        | Choice        | Why |
|-------------|----------------|-----|
| Language    | Python 3.11+   | Standard for quant/finance; great libs (pandas, numpy, requests). |
| Database    | SQLite         | Zero config, single file, easy to move to Postgres later. |
| Viz         | Streamlit      | Fast dashboards in Python; iterate quickly and learn from the data. |
| Deps        | pandas, yfinance, requests, PyYAML | Minimal set to fetch, normalize, and store. |

### Platform evolution (steering)

Stack choices above are the **MVP1 baseline**. Growth is **by layer** (API, DB, auth, UI), not a single swap. Triggers and agent STOP rules: [`docs/SOP/PLATFORM_EVOLUTION_V1.md`](SOP/PLATFORM_EVOLUTION_V1.md).

No API keys required for the initial data sources below (except optional CoinGecko for higher rate limits).

---

## Data Sources

### Markets (prices / implied info)

1. **Yahoo Finance (yfinance)**  
   - **Gold**: `GC=F` (front-month futures), `GLD` (ETF).  
   - **Silver**: `SI=F` (futures), `SLV` (ETF).  
   - **Bitcoin**: `BTC-USD` (spot).  
   - Gives OHLC, volume; we can add options/vol later for implied probabilities.

2. **CoinGecko (optional)**  
   - Backup or extra crypto (BTC, ETH). Free tier works without key for light use; add key later if we hit limits.

### Prediction markets

3. **Polymarket**  
   - **Gamma API** (`https://gamma-api.polymarket.com`): list events/markets, tags, search.  
   - **CLOB API** (`https://clob.polymarket.com`): prices, order book, price history.  
   - Markets have `outcomePrices` → implied probabilities. We’ll filter for crypto/macro/commodity-related events.

Later: **Kalshi** (US regulatory, macro), **China**-oriented prediction markets or indices when we add that theme.

---

## Canonical Events (v1)

We define a small set of **canonical events** so we can compare “same event” across market data and prediction markets.

### Asset-based (Gold, Silver, Bitcoin)

| Canonical event ID   | Description (example)           | Market data we use        | Prediction markets we’ll match |
|----------------------|---------------------------------|---------------------------|---------------------------------|
| `gold_above_X`       | Gold (spot/futures) above $X by date Y | GC=F, GLD (yfinance)     | Polymarket markets mentioning “gold” / price levels |
| `silver_above_X`     | Silver above $X by date Y       | SI=F, SLV (yfinance)     | Polymarket “silver” / price    |
| `bitcoin_above_X`    | Bitcoin above $X by date Y      | BTC-USD (yfinance)       | Polymarket “Bitcoin” / price   |

We’ll store:
- **Threshold + resolution date** (e.g. “Bitcoin above 100000 by 2025-12-31”).
- **Source**: `market` (from price/vol) or `prediction_market` (Polymarket).
- **Implied probability** and **timestamp**.

### Derived / cross-asset (later)

- **BTC vs gold**: e.g. “BTC outperforms gold over period” (ratio or total return).
- **Silver vs gold**: “Silver outperforms gold” (spread or ratio).
- **China**: add when we add China data (e.g. Shanghai Composite, CNY, or China-focused prediction markets).

### How we’ll use them

- **Level 1**: Same canonical event (e.g. “BTC > 100k by EOY”) → compare Polymarket probability vs implied from options/spot (when we add it) → flag arb / near-arb / high-prob.  
- **Level 2**: Combine events (e.g. gold up + silver up → “precious metals rally”) and derive implied probabilities for composite outcomes.  
- **Viz**: Dashboards by canonical event (time series of probabilities by source) and by opportunity type.

---

## Repo layout (high level)

```
config/          # symbols, event definitions, source URLs
src/
  data/           # fetchers (yfinance, Polymarket Gamma/CLOB)
  models/         # DB schema, canonical event types
  engine/         # probability layer, arb/opportunity detection
  viz/            # Streamlit app
docs/             # this plan, later design notes
```

Next: implement fetchers, normalize to canonical events, then wire engine + Streamlit.
