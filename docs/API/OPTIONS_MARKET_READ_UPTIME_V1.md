# Options Market Read production uptime check

Extends the existing **Uptime healthcheck** workflow (`.github/workflows/uptime-healthcheck.yml`). It does not create a second monitor and does not depend on a ChatGPT automation.

## Schedule

The workflow already runs every **30 minutes** and on **workflow_dispatch**. The Options Market Read synthetic check rides that job, so it runs at least hourly and can be triggered manually from GitHub Actions.

## What it validates

Both production URLs:

- `https://marketstructureos.com/v1/options-market-read`
- `https://marketstructureos.com/ppe-display-api/display.json?asset=BTC&depth=full`

Required:

- HTTP 200 JSON
- `schema_version` and `ruleset_version` present
- `asset` is BTC
- `answer` nonempty
- `resolved_expiry` present
- `as_of` valid and no more than 25 minutes old
- required price, range, and volatility values present and finite
- spot, selected-expiry ATM IV, and q25/median/q75 agree with `display.json` after documented public rounding
- range width equals rounded high minus rounded low

If snapshot times differ between the two requests, the pair is retried before failing. Transient network errors use bounded retries and a 30s timeout.

Failure output is actionable: check name, observed values, UTC check time, and URL.

## Alerting

The established mechanism is a **failed GitHub Actions run** (Actions UI plus whatever GitHub notification routing is already enabled). This workflow does not send ntfy, SMS, email webhooks, or any external destination, and it does not invent credentials.

**Founder/platform choice still required** for durable phone/push alerting: either route GitHub workflow-failure notifications to an on-call inbox, or add a repository secret for an existing ntfy topic and wire it into this workflow. Do not add a new alert vendor in code until that choice is made.

## Local

```bash
python scripts/options_market_read_uptime.py
python -m pytest -q tests/test_options_market_read_uptime.py
```
