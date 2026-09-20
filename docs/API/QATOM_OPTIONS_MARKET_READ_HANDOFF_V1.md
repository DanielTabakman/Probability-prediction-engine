# Qatom handoff: Options Market Read v1.3

## What this gives Qatom

Options Market Read answers one bounded question: **what is the BTC options
market pricing for a selected time?** It returns a deterministic, two-sentence
plain-English summary plus structured numbers for spot, the options-implied
center, the middle 50% of priced outcomes, and relative priced uncertainty.

It is informational. It does not forecast BTC, recommend an exposure, rank an
opportunity, construct a strategy, execute a trade, or handle payment.

## Integration URLs

| Purpose | URL |
|---|---|
| Production API — use in Qatom | `https://marketstructureos.com/v1/options-market-read` |
| Human staging console — use for joint testing | `https://staging.marketstructureos.com/options-market-read` |
| Staging API — test only | `https://staging.marketstructureos.com/v1/options-market-read` |
| Human help | `https://staging.marketstructureos.com/options-market-read/help` |
| Machine-readable help | `https://staging.marketstructureos.com/options-market-read/api-help` |

Qatom should call production in released code. Staging can change and is kept
separate so dates, errors, and future revisions can be tested without changing
the production response.

## Request

`GET /v1/options-market-read`

| Parameter | Required | Meaning |
|---|---:|---|
| `asset` | No | Defaults to `BTC`; BTC is the only enabled asset in v1.3. |
| `target_date` | No | ISO calendar date `YYYY-MM-DD`. If omitted, the target is the snapshot date plus 30 days. |

```bash
curl -H "Accept: application/json" \
  "https://marketstructureos.com/v1/options-market-read?asset=BTC&target_date=2026-12-25"
```

Options contracts have listed expiries. An exact date wins. Otherwise the API
uses the nearest live expiry within 14 days, with a tie going to the later
expiry. Qatom should show both `effective_target_date` and `resolved_expiry`
when `expiry_resolution` is not `exact`.

## What to render

1. Show `answer` first. It contains the useful human summary and exact UTC
   snapshot time.
2. Use `metrics` for cards or calculations: `spot_price`,
   `median_terminal_price`, `middle_50_range`, and `atm_iv_percent`.
3. Show the selected contract from `resolved_expiry`; do not label the requested
   date as an expiry unless `expiry_resolution` is `exact`.
4. Put `disclosures` behind an expandable “method and limitations” control.
5. Treat `as_of` as the market-data timestamp and warn or retry if it is more
   than 25 minutes old.

The API response is the contract. The human console's date parser is only a UI
helper and is not part of the JSON API.

## Errors and compatibility

| HTTP | Code | Consumer behavior |
|---:|---|---|
| `422` | `unsupported_asset` | Explain that v1.3 supports BTC only. |
| `422` | `past_target_date` | Ask for the snapshot date or a future date. |
| `422` | `expiry_not_close_enough` | Offer the nearest dates from `error.details`, if present. |
| `503` | data/snapshot error | Do not show a stale interpretation as current; retry later. |

Integrate against `schema_version: "1.3"` and
`ruleset_version: "options-market-read.v1.3"`. Ignore additive unknown fields.
Do not infer direction from implied volatility. The same snapshot and request
produce byte-identical JSON; no LLM generates the response.

## Tuesday acceptance checklist

- Confirm the Qatom surface and exact wording used to ask for an asset/date.
- Confirm Qatom can call production HTTPS and parse a 200 JSON response.
- Test omitted date, exact expiry, nearest expiry, unsupported ETH, past date,
  and a date more than 14 days from a supported expiry.
- Confirm Qatom displays `answer`, `resolved_expiry`, freshness, and disclosures
  in the intended hierarchy.
- Decide whether partner authentication, rate limiting, or CORS is needed before
  wider release; none should be assumed from this preview.
- Record any desired additive fields as a versioned contract change rather than
  rewriting the existing v1.3 fields.
