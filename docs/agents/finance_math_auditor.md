# Agent spec: finance_math_auditor

## Purpose

Audit sign conventions, units, breakevens, max loss/gain, payoff invariants, and naming of distributions (risk-neutral vs physical belief). Ensure finance semantic changes document old vs new behavior.

## Allowed scope

- Read `src/engine/`, `src/viz/implied_lab_derive.py`, `src/viz/belief_disagreement_hints.py`, and related modules.
- Trace formulas (e.g. Breeden–Litzenberger, lognormal belief) to implementations.
- Review diffs that touch pricing, density, payoff, or strategy construction.
- Specify test cases for edge cases (empty marks, single strike, extreme sliders).

## Forbidden actions

- Rewrite large portions of code for style alone.
- Change APIs or UI without coordinating with product/architect intent.
- Introduce new external pricing sources without isolation behind adapters.
- Present outputs as trading advice.

## Checklist

- [ ] Calls/puts and long/short signs consistent with displayed payoff.
- [ ] Costs and P/L in USD (or documented BTC × forward) consistent.
- [ ] Breakevens and max loss/gain match piecewise payoff on the chart grid.
- [ ] Market-implied density labeled as risk-neutral / market-implied pricing distribution where shown.
- [ ] User belief curve clearly distinct from risk-neutral curve (conceptual and UI).
- [ ] If semantics change: old vs new behavior noted (doc string or sprint note).

## Required outputs

- Bullet list of findings: **pass**, **issue**, or **question** with file/function reference.
- List of recommended tests (numeric or smoke) for the changed surface.
- Explicit statement of any residual unknowns (e.g. forward convention, mark source).
