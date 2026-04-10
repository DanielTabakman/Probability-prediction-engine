# ORIGINAL_SPEC

Purpose: stable description of the intended product target for the current build cycle. Synthesized from `README.md`, `docs/PLAN.md`, `docs/SPRINT_1_SPEC.md`, and `docs/SEMANTIC_CONTRACTS.md`—not a new product definition.

## Product / website goal
A **probability prediction engine** that cross-references **market data** (stocks, crypto, commodities/futures) and **prediction markets** (e.g. Polymarket) to surface arbitrage, near-arbitrage, and high-probability angles—eventually with derived questions and richer automation. **Near term**, the focus is a **Streamlit**-based **viz layer** and a **manual implied lab**: explore market-implied distributions, optional user belief, disagreement structure, and strategy-family fit—with honest labeling (priced/risk-neutral vs “true belief”).

## Core user experience
- **Ingestion & canonical events** (directional): same-style events (e.g. gold/silver/Bitcoin level-by-date) comparable across market and prediction-market sources (`docs/PLAN.md`).
- **Implied lab (current UX thrust)**: one primary screen where a user quickly sees **what the priced market implies**, **what belief inputs they are changing**, **how payoff changes**, and **key trade stats**—with mode switches (exact strikes vs target payoff; market vs user belief vs compare) and advanced detail tucked away (`docs/SPRINT_1_SPEC.md`, `docs/SEMANTIC_CONTRACTS.md`).

## Must-have elements
- Centralized derivation of **visible lab outputs** from shared state—not duplicated widget logic (`docs/SPRINT_1_SPEC.md`).
- **Clear semantics** in UI copy: market-implied **pricing/risk-neutral** distribution vs **user belief**; **disagreement** as descriptive; strategy families as **explore/fit**, not “recommended trade” unless an explicit advisory layer exists (`docs/SEMANTIC_CONTRACTS.md`).
- **Testable paths**: unit tests where logic lives; smoke/launch-and-inspect for user-visible changes (see `HANDOFF.md`, `docs/IMPLIED_LAB_SMOKE.md`).

## Must-not-break elements
- Honest distinction between **verified** behavior and **inferred** behavior in reports and docs.
- **Semantic contracts** for disagreement, strategy family, and market-implied vs belief language—do not silently recast meanings.
- Working **local run** story: venv, `requirements.txt`, `streamlit run src/viz/app.py` (`README.md`).

## Out of scope (current cycle unless explicitly reopened)
- New **AI** features, **prediction-market** wiring beyond stated plan, **framework migration** (`docs/SPRINT_1_SPEC.md`).
- Major **new strategy logic** unless required for layout/state clarity (`docs/SPRINT_1_SPEC.md`).

## Acceptance picture
“We match the original intent” means: the **implied lab** matches **Sprint 1** layout and comprehension goals (chart up top, two-column layout, summary stats, mode/belief switches, math behind expanders); wording and concepts stay aligned with **SEMANTIC_CONTRACTS**; and the **README/PLAN** vision (engine + viz + canonical events) remains the north star without unapproved scope creep.

## Notes
Longer-term roadmap phases (arb detection, broader dashboards, AI/trading) live in `README.md` / `docs/PLAN.md`; **ORIGINAL_SPEC** tracks what this cycle is building **toward**, not every future phase.
