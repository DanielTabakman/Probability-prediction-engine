# Forward Consistency v1 — SELECTION

**Chapter:** `forward_consistency_v1`  
**Program:** [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md)  
**Relay:** [`PHASE_PLANS/forward_consistency_v1_relay.json`](PHASE_PLANS/forward_consistency_v1_relay.json)

---

## Status

**SELECTED** 2026-06-28 — core spine (engine + API + Strategy Lab panel).

**Pre-build:** Implementation on [`PR #447`](https://github.com/DanielTabakman/Probability-prediction-engine/pull/447) (`build/forward-consistency-v1`). BUILD slice verifies merge, gate, evidence.

---

## Rationale

Answer: *For this asset/expiry (Deribit BTC/ETH), are synthetic forward and dated future bid/ask consistent after costs?*

Bid/ask only. Research-only. Uses existing Strategy Lab asset picker + expiry.

**Blocked until:** `forward_consistency_charter_v1` **COMPLETE**.

---

## Non-goals

- Bybit SOL, secondary surfaces, archive, execution
