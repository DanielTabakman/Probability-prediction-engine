# Research Decision Dashboard v0 — Codex implementation packet

**THREAD_ROLE:** `codex_build`  
**Chapter:** `ppe_research_decision_dashboard_v0`  
**Program:** [`RESEARCH_DECISION_DASHBOARD_PROGRAM_V1.md`](RESEARCH_DECISION_DASHBOARD_PROGRAM_V1.md)  
**SELECTION:** [`POST_RESEARCH_DECISION_DASHBOARD_V0_SELECTION.md`](POST_RESEARCH_DECISION_DASHBOARD_V0_SELECTION.md)

## Goal

Implement a small, read-only, feature-flagged Streamlit Research Review surface that accurately explains the accepted hedge-backed event liquidity Stage 0/0.1 decision chain.

## Why this matters

The current reports are reproducible but difficult for the founder to interrogate. The UI must make the theory, tested gates, blocked work, untested economics, recommendation, and reopen conditions immediately legible without changing the underlying research conclusion.

## Canon / relevant documents

Read only these before editing:

- `docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`
- `docs/SOP/RESEARCH_DECISION_DASHBOARD_PROGRAM_V1.md`
- `docs/SOP/POST_RESEARCH_DECISION_DASHBOARD_V0_SELECTION.md`
- `docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`
- `docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_1_TERMINAL_AVAILABILITY_REPORT_V1.md`
- `src/viz/app.py`
- `src/viz/app_sidebar.py`
- `scripts/hedge_backed_event_stage0_1_terminal_witness.py`
- relevant existing UI smoke patterns only as needed

Do not rediscover or redesign the entire repository.

## Relevant code paths

Expected ownership:

- `src/viz/research_decision_dashboard.py` or an equivalently small pure model/loader module;
- `src/viz/research_decision_view.py` or an equivalently small Streamlit renderer;
- `src/viz/app.py`;
- `src/viz/app_sidebar.py` only if needed for the feature-flagged entry point;
- `fixtures/research_decision_dashboard/hedge_backed_event_liquidity_stage0_1_v1.json`;
- `tests/test_research_decision_dashboard.py`;
- `scripts/run_research_decision_dashboard_smoke.py` and minimal supporting smoke fixture/harness files;
- docs required to record validation evidence.

Avoid touching MSOS frontend routes, execution code, wallets, venue adapters, or control-plane queue/manifest files unless the packet is formally revised.

## Current behavior

- The existing Streamlit app displays market data, implied distribution, options/futures overlays, and related research information.
- Hedge-backed event liquidity evidence exists in reports and artifacts but has no coherent founder-facing dashboard.
- The accepted recommendation is `STOP_POLYMARKET_BRANCH`.
- Profitability, executable hedge construction, shadow execution, and live execution were not demonstrated.

## Required behavior

### Feature flag

Use:

```text
PPE_RESEARCH_REVIEW_UI=1
```

When false or absent, default app behavior and sidebar must remain unchanged.

### Data contract

Implement and validate `ResearchDecisionDashboardV1` with the fields defined by the program. Prefer dataclasses, TypedDict, or explicit validation consistent with repository patterns. Keep interpretation in the fixture/model rather than the Streamlit renderer.

### Deterministic fixture

Create a committed JSON fixture representing accepted Stage 0.1 evidence. It must include:

- theory status: plausible, not economically tested;
- Polymarket branch: stopped;
- profitability: `NOT_TESTED`;
- execution: `NOT_AUTHORIZED`;
- recommendation: `STOP_POLYMARKET_BRANCH`;
- funnel counts: 1,100 general objects, 7 frozen candidates, 0 eligible, 0 synthetic hedges, 0 executable discrepancies, 0 shadow trades;
- gate statuses from the program;
- all seven candidate questions and rejection reasons;
- interpretation and reopen conditions;
- PRs `#5384`, `#5385`, `#5386`;
- accepted merge commit `e162a4dc48a8c724d37502ca90bdebe49029d493`;
- canonical report paths and witness timestamp.

Do not claim 1,100 semantic contract reviews. The fixture must state that seven BTC threshold candidates were frozen and semantically inspected from the broader discovery envelope.

### UI

Render, in order:

1. Decision/status header.
2. Theory and mechanism.
3. Funnel.
4. Gate matrix.
5. Candidate inspector.
6. Interpretation and reopen conditions.
7. Provenance and warnings.

Use plain, legible Streamlit components. Avoid decorative work that does not improve comprehension.

### Semantic safeguards

The page must never display:

- `BLOCKED` as `FAIL`;
- `NOT_TESTED` as `FAIL`;
- `NOT_AUTHORIZED` as `NOT_TESTED`;
- `STOP_POLYMARKET_BRANCH` as rejection of the general theory;
- any quote/trade recommendation;
- any indication that a hedge or profitability test was completed.

### Network and mutation boundary

The accepted fixture must render with network access disabled. The renderer must not call Polymarket, Deribit, or any other external service. The page must contain no state-changing action beyond ordinary local Streamlit UI state.

## Constraints

- Keep implementation small and reversible.
- Preserve import policy: pure modules should be testable without importing `src.viz.app`.
- Streamlit-only code belongs in the renderer.
- Use the existing repository environment flag helper where appropriate.
- Do not add a generic multi-initiative registry or persistence database in v0.
- Do not edit accepted Stage 0/0.1 reports to fit the UI.
- Do not change the `STOP_POLYMARKET_BRANCH` recommendation.

## Non-goals

- Live data refresh.
- Scheduled collection.
- Market creation.
- Venue submission.
- Trading, quoting, order entry, wallets, custody, or treasury.
- MSOS customer-facing route.
- General-purpose governance platform.
- Automatic natural-language interpretation by an LLM.

## Acceptance criteria

Use the twelve acceptance criteria in the program as authoritative. In addition:

1. A unit test must assert the exact status distinction for the first fixture.
2. A unit test must assert that the funnel contains `1100`, `7`, `0`, and `0` with the correct labels.
3. A unit test must assert seven candidates and zero `ELIGIBLE` outcomes.
4. A unit test must reject an invalid or unknown gate state.
5. A smoke witness must confirm the page contains:
   - `STOP_POLYMARKET_BRANCH`;
   - theory not disproven / plausible-not-tested language;
   - profitability not tested;
   - execution not authorized;
   - seven frozen candidates;
   - zero eligible contracts.
6. Default app smoke remains green with the feature flag disabled.

## Validation commands or evidence

Run and include exact outputs in the draft PR:

```powershell
python -m pytest -q tests/test_research_decision_dashboard.py
python scripts/run_research_decision_dashboard_smoke.py
python scripts/run_implied_lab_ui_smoke.py
python scripts/run_pushable_gate.py
python scripts/run_pushable_gate.py --pre-push
```

If a command is not applicable because of a repository-specific harness limitation, do not silently omit it. Explain the limitation and provide the closest reproducible evidence.

## Ownership / overlap warning

Before editing, check for open work touching:

- `src/viz/app.py`;
- `src/viz/app_sidebar.py`;
- Streamlit smoke harnesses;
- research control-plane artifacts.

If overlap exists, stop and report it. One writer only.

## Required PR behavior

- Work on a dedicated implementation branch.
- Open a draft PR.
- Do not merge.
- Include changed paths, exact validation evidence, screenshot or structured smoke evidence, and the mandatory block below.

```text
COORDINATION STATUS
Agreement: <aligned | partial | conflict | unknown>
Compared: program, SELECTION, packet, accepted Stage 0/0.1 reports, changed files, tests and smoke
Disagreement: <none or concise statement>
Evidence gap: <none or missing proof>
Ownership overlap: <none or paths/state>
Risk if unresolved: <none or consequence>
Recommended default: <one action>
Founder decision required: yes | no
```

## Handoff completion condition

Return the draft PR number and head commit. Regular Chat will independently inspect the implementation and evidence. Do not declare the chapter accepted or merge the PR.