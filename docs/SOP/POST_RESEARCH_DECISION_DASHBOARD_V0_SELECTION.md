# Research Decision Dashboard v0 — SELECTION

**Chapter:** `ppe_research_decision_dashboard_v0`  
**Program:** [`RESEARCH_DECISION_DASHBOARD_PROGRAM_V1.md`](RESEARCH_DECISION_DASHBOARD_PROGRAM_V1.md)  
**Implementation packet:** [`RESEARCH_DECISION_DASHBOARD_V0_CODEX_PACKET.md`](RESEARCH_DECISION_DASHBOARD_V0_CODEX_PACKET.md)  
**As-of:** 2026-07-18

## Status

**SELECTED** by founder for bounded implementation.

The selected outcome is a reusable operator-only research review surface, beginning with the accepted hedge-backed event liquidity Stage 0/0.1 evidence.

## Why selected

The accepted research was reproducible but not sufficiently legible for founder review. The terminal recommendation `STOP_POLYMARKET_BRANCH` did not itself make clear that:

- the general options–prediction-market crossover theory was not disproven;
- Polymarket contract inventory failed the terminal-payoff gate;
- hedge economics and profitability were never tested;
- execution was not authorized;
- the branch can be reopened only after a qualifying contract universe exists.

This is a recurring governance need, and more strategy research is planned.

## Selected scope

1. Versioned research-decision JSON contract.
2. Deterministic fixture for hedge-backed event liquidity Stage 0.1.
3. Pure Python loader/presentation model.
4. Feature-flagged Streamlit operator surface.
5. Funnel, gate matrix, candidate inspector, interpretation, and provenance.
6. Unit tests and dedicated UI smoke witness.
7. Independent regular-Chat review before merge.

## Required semantics

The implementation must preserve these distinctions:

- theory status versus venue/branch status;
- `FAIL` versus `BLOCKED`;
- `NOT_TESTED` versus `FAIL`;
- `NOT_AUTHORIZED` versus `NOT_TESTED`.

The first fixture must visibly state:

```text
theory: plausible, not economically tested
Polymarket branch: stopped
profitability: not tested
execution: not authorized
```

## Non-goals

- No live trading or order routing.
- No customer-facing route or default navigation.
- No live network calls during dashboard render.
- No restart of the Polymarket hedge-scanner branch.
- No multi-initiative registry framework in v0.
- No scheduled archive or decision-history collector.
- No authorization to create, seed, manipulate, or trade a prediction market.

## Acceptance

The chapter is accepted only when all program acceptance criteria pass, the implementation PR contains reproducible validation evidence, and independent review confirms that the dashboard accurately represents PRs `#5384–#5386` and accepted merge commit `e162a4dc48a8c724d37502ca90bdebe49029d493`.

## Next initiative after acceptance

Prepare a separate charter for **issuer-created hedgeable event markets**. That charter must begin with venue permission, market-creation mechanics, market-integrity/conflict controls, settlement design, liquidity requirements, and legal/terms review before economic backtesting or implementation.