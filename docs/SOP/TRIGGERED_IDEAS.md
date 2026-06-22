# Triggered ideas

**Purpose:** Park "great idea, too early" items with revisit triggers. They surface when a matching chapter enters SELECTION — dismiss when processed.

| Command | Action |
|---------|--------|
| `triggered_ideas.cmd` | List active parked ideas |
| `python scripts/ppe_triggered_ideas.py add ...` | Park a new idea |
| `python scripts/ppe_triggered_ideas.py dismiss <id>` | Done — hide from active list |
| `python scripts/ppe_triggered_ideas.py dismiss <id> --purge` | Remove + archive one line |

**Machine source:** [`TRIGGERED_IDEAS.json`](TRIGGERED_IDEAS.json) · **Alert artifact:** `artifacts/control_plane/TRIGGERED_IDEAS_ALERT.json`

> Park ideas with revisit triggers — surfaced when a matching chapter/plan enters SELECTION. Dismiss when processed: python scripts/ppe_triggered_ideas.py dismiss <id> [--purge]

## Active (parked / surfaced)

### Revisit Uniblock vs single Web3 provider

- **id:** `web3_uniblock_revisit` · **priority:** low · **status:** parked
- **added:** 2026-06-15
- **summary:** Deferred 2026-06-15. Not needed for Deribit/Polymarket/Yahoo or Cloudflare Access email accounts. Revisit when charter includes wallet connect or on-chain per-user reads.
- **trigger chapterIds:** `msos_wallet_connect_v1`, `msos_onchain_portfolio_v1`
- **trigger keywords:** wallet connect, walletconnect, on-chain portfolio, web3 provider, uniblock
- **not for:** `msos_user_state_v1`, `msos_workflow_persistence_v1`, `msos_access_identity_v1`, `msos_billing_lemon_squeezy_v1`

## Changelog

| 2026-06-21 | Auto-render from JSON |
