# Market Structure OS — Product Semantics & State Model v0.1

## Canonical hierarchy

- **Market Structure OS / MSOS**: company and software platform.
- **Command Center**: authenticated home/dashboard where users see active work, alerts and history.
- **Strategy Lab**: workspace where users design, test and monitor thesis-driven market strategies.
- **PPE**: first tool built inside the Strategy Lab; probability/thesis comparison engine.
- **Lens**: a specific market-surface interpretation mode, such as options distributions, event probabilities, or leverage/positioning.
- **Thesis**: the user's human-owned belief about what is mispriced or likely.
- **Expression**: a structure or exposure family that fits a confirmed thesis under selected constraints.
- **Execution rail**: a venue or integration through which action may eventually occur.
- **Monitoring plan**: alerts tracking thesis validity, expression risk and data/trust state.
- **Calibration memory**: history of observed, saved, simulated, executed and reviewed theses.

## Lifecycle state model

Exploring -> Draft thesis -> Confirmed thesis -> Expression saved -> Simulated or Executed -> Monitoring -> Reviewed / Resolved

**Interaction modes (orthogonal):** Why the user opened MSOS *now* — Disagreement, Expression Search, Hedging, Scenario Planning, Timing, Monitoring, Learning/Review. Lifecycle states describe *where a thesis is*; interaction modes describe *user intent*. Full taxonomy: [`MSOS_Market_Interaction_Modes_v0.1.md`](../../MSOS_Market_Interaction_Modes_v0.1.md) (vision only — not current build scope).

## Build rules for Cursor

1. Do not use PPE as the company/platform identity. PPE is the first tool.
2. Do not describe a suggested expression as a guaranteed or recommended trade. Use “optimized expression plan” or “suggested expression” with assumptions visible.
3. Keep thesis, expression, execution, monitoring and review as separate states in the data model and UI.
4. Use Live / Soon / Planned labels whenever a lens or rail is not actually available.
5. Execution rails must be instrument-compatible. Deribit can be eligible for an options structure; Hyperliquid is pending for future perps/positioning, not an equivalent options execution venue.
6. All reference models must be named or inspectable. “Reference” is not hidden authority.
7. Use plain-English gaps: e.g., “Your range is 21% narrower than market pricing.”
