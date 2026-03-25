# CURRENT FRONTIER

## Product north star
Build a market legibility and view-expression lab that:
1. explains the market-implied pricing distribution,
2. lets the user express a different belief,
3. compares belief vs market,
4. maps disagreement to strategy families and exact structures,
5. shows full calculations and source-backed verification.

## Current build frontier
We are currently focused on:

**Phase 2.5 → 3**
- user belief vs market comparison
- disagreement explanation
- strategy-family mapping
- exact strikes and target payoff workflows
- calculation transparency and verification

We are **not yet** building:
- full prediction market correlation engine
- automated statistical arbitrage scanner
- broad multi-asset event graph
- autonomous AI trade agent

## Current user promise
The app should help a user:
- see what the options market is pricing at a chosen expiry,
- overlay their own belief,
- understand the biggest differences,
- explore strategy families and exact structures,
- verify the math and market references.

## Accepted current behaviors
- **Current sprint:** iteration loop — BTC implied lab auto-loads (no separate “run” click); optional Deribit chart overlays via **Refresh priced inputs (Deribit)**; belief sliders are not reset by refresh.
- Streamlit app runs with BTC implied distribution lab
- exact strikes mode works
- target payoff mode works
- user belief overlay exists
- disagreement summary exists
- trade ticket and calculation panels exist
- supporting reference sections exist

## Current design principles
1. Clarity
2. Playability
3. Verifiability

## Current highest-EV unanswered questions
1. What is the canonical disagreement object?
2. What is the canonical strategy-family object?
3. How should the app distinguish “fit” from “recommendation”?
4. What verification path should every displayed value support?

## Next sprint target
Create canonical domain contracts for:
- market-implied belief comparison
- strategy-family hints
- UI rendering from structured objects instead of loose strings

## Constraints
- one sprint frontier at a time
- minimal diffs
- no silent semantic drift
- preserve current working behavior unless explicitly changed
- commit + push only after accepted sprint

## Definition of done for current frontier
A user can go from:
**market view → personal view → disagreement → fitting structures → verification**
without semantic confusion.