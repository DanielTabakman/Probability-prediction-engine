# Market Proposal + Hedge Capacity Preview v0 — SELECTION

**Chapter:** `ppe_market_proposal_hedge_capacity_preview_v0`  
**Program:** [`MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_PROGRAM_V1.md`](MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_PROGRAM_V1.md)  
**Implementation issue:** `#5391`  
**As-of:** 2026-07-18

## Status

**SELECTED AS THE NEXT PRODUCT STEP.**

Product-code implementation is blocked until the Research Decision Dashboard in `#5388` is implemented and independently accepted.

## Selected outcome

A small operator/demo tool that:

- takes a desired terminal BTC event;
- generates deterministic, hedge-aligned question and resolution language;
- selects adjacent-strike Deribit vertical-spread hedge candidates;
- calculates current executable hedge capacity from order-book depth;
- shows requested, supported and unsupported payout size;
- displays cost stack, payoff ramp, residual mismatch and all material constraints;
- exports a shareable Markdown and JSON proposal.

## Why selected

The founder wants a concrete object to show prospective customers and venues before deciding whether to build a broader prediction-market liquidity service.

The accepted Polymarket research established that waiting for suitable terminal contracts is insufficient. This step tests whether MSOS can originate a coherent question from the available hedge rather than merely scan whatever markets already exist.

## Required product truth

The preview must say what is actually known:

```text
question: proposed, not listed
hedge capacity: snapshot estimate, not guaranteed fill
binary replication: approximate across a visible strike ramp
requested size: partly or fully supported only at the stated prices/depth
prediction venue costs and demand: unknown in v0
market creation and trading: not performed
```

## Boundaries

No market submission, market deployment, customer outreach automation, option orders, prediction-market orders, wallet access, custody, treasury movement, capital reservation, or arbitrage claim.

Manual sharing of an accepted export is allowed after founder review.

## Mandatory stop

After the implementation is independently accepted, no next chapter starts automatically.

Regular Chat and the founder must review:

- what the live hedge capacities actually look like;
- whether the proposed questions are understandable and attractive;
- which constraints dominate;
- whether to show the preview to customers or venues;
- whether to change product direction, run customer discovery, pursue listing access, or stop.

## Acceptance

Acceptance requires every criterion in the program, a draft implementation PR with reproducible evidence, and independent regular-Chat review with the mandatory Coordination Status block.

## COORDINATION STATUS

```text
COORDINATION STATUS
Agreement: aligned
Compared: founder direction, merged dashboard charter #5387, open dashboard implementation #5388, issuer-created market issue #5389, selected implementation issue #5391, accepted Stage 0/0.1 evidence
Disagreement: none
Evidence gap: implementation, live order-book capacity, exported proposal and customer response do not exist yet
Ownership overlap: implementation must wait for #5388 acceptance before touching shared Streamlit paths
Risk if unresolved: the demo could overstate available hedge depth or obscure the finite-width replication mismatch
Recommended default: implement the bounded preview after #5388, independently review it, then stop for founder discussion
Founder decision required: no
```