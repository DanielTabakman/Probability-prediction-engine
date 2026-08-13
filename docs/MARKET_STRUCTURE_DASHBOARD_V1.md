# Market Structure Dashboard v1

**Status:** Proposed founder-facing UX contract
**Scope:** Dashboard/project visibility only. No strategy math, detector tuning, or execution changes.
**Implementation surface:** MSOS Mission Control
**Future research-state owner:** `market-structure-engine`

## Goal

Mission Control should behave like a project briefing that includes live evidence, not like a telemetry dashboard that happens to contain a project.

A founder must be able to answer in seconds:

1. What is this?
2. Where are we?
3. What are we testing?
4. What did we learn?
5. What is blocked?
6. What happens next?
7. What is running?
8. Where is the work?

## Required founder-facing state

### MARKET STRUCTURE ENGINE

**Purpose**
Find meaningful market structure across scales without choosing one arbitrary timeframe first.

**Current stage — Validating detected structure**

- 🟢 Data collection
- 🟢 Multi-scale analysis
- 🟡 Validate detected levels
- ⚪ Predictive validation
- ⚪ Strategy integration
- ⚪ Execution integration

**Current question**
Do persistent multi-scale levels contain useful information about what happens next?

**Current experiment — Multi-scale level validation v0**
We detected support/resistance candidates independently across multiple horizons and found levels that persist across scales. Now determine whether those levels correspond to meaningful subsequent market behaviour.

Not testing yet: profitability, automatic trade signals, strategy execution, or one privileged timeframe.

## What we learned

Retain these findings in a compact research ledger:

- Data quality is scale-dependent.
- NDAX 5m = POOR.
- NDAX 15m = MARGINAL.
- NDAX 1h = USABLE.
- NDAX 4h = USABLE.
- NDAX 1d = PROVISIONAL because the first live witness did not yet include a full 24h of capture history.
- Persistent cross-scale candidate levels exist.
- Candidate levels are not validated predictive signals.
- No trade signal is currently generated.

Preserve corrections explicitly:

- Rejected: `NDAX is bad data.` Replacement: usefulness depends on scale.
- Rejected as default workflow: `Choose the correct timeframe first.` Replacement: evaluate across scales first, then learn which horizons are informative.

## Blocked

**No critical blockers.**

Current limitation: 1d evidence is provisional due to immature capture history in the first witness.

Future integrations such as Hummingbot, strategy wiring, execution wiring, or the repo split are not blockers for the current validation step.

## Next

**Validate whether persistent levels correspond to meaningful future price interactions.**

Supporting copy: inspect candidate levels against subsequent price behaviour, then move to forward/out-of-sample validation before any strategy or execution dependency.

The primary page must show one dominant next action, not a backlog.

## Recent results

Default founder-facing summary:

| Scale | Fit |
|---|---|
| 5m | 🔴 POOR |
| 15m | 🟡 MARGINAL |
| 1h | 🟢 USABLE |
| 4h | 🟢 USABLE |
| 1d | 🟡 PROVISIONAL |

Headline evidence:

- Persistent structure detected: Yes
- Strongest candidate: 105.507 CAD — 1h + 4h + 1d — 11 touches
- Second candidate: 104.713 CAD — 15m + 1h + 4h — 8 touches
- Trade signal: None

## What is running

Use human-readable purpose labels:

- 🟢 Signal Capture — collecting live NDAX market observations.
- 🟢 Multi-scale analysis — evaluating 5m / 15m / 1h / 4h / 1d.
- 🟢 Mission Control staging — showing current research state and live evidence.

Do not expose internal JSON paths, container names, environment variables, service plumbing, or internal field names on the primary interface.

## Where is the work?

- Research engine: `market-structure-engine` — proposed future canonical research/engine home.
- Current MSOS experiment: `DanielTabakman/Probability-prediction-engine` PR #5411.
- Current capture experiment: `DanielTabakman/poroburu-oct-signal-capture` PR #2.
- Live witness: 2026-08-13 multi-scale NDAX witness.
- Dashboard: MSOS Mission Control staging.

Capture PR #2 is closed and unmerged even though its branch produced the live witness. Treat the runtime witness as evidence, not as final canonical architecture.

## Exact page order

1. Header: MARKET STRUCTURE ENGINE + purpose.
2. Six-stage status ladder with exactly one current stage.
3. Current question.
4. Current experiment + `Not testing yet`.
5. What we learned: retained findings + rejected/updated hypotheses.
6. Next: one visually dominant action.
7. Blocked: `No critical blockers` unless fresh evidence creates one.
8. Recent results: simplified scale ladder + 2–3 headline levels.
9. What is running: human-readable service purposes.
10. Where is the work: repo/PR/witness/deployment links.
11. Technical details: collapsed by default.

## Keep / move / remove

**Keep on the primary page**
- live capture status in human language
- scale fitness labels
- strongest candidate levels
- read-only / no-trade-signal boundary
- one next action
- staging/live status

**Move under Technical details**
- observation counts
- range / spread / spread-to-range
- max gaps
- zone counts
- full level list
- detector method
- source file counts
- auto-refresh detail
- Jupiter telemetry if still useful for engineering

**Remove from the primary narrative**
- Observe / Understand / Decide / Execute / Learn as the main hierarchy
- `OCT / Hummingbot test` as project identity
- prominent Hummingbot current-stage card
- stale `inspect the first multi-scale map` next action
- implementation field names

## Project-state contract

Durable project/research state and live telemetry must be separate inputs.

Minimum semantic shape:

```ts
type MarketStructureProjectState = {
  project: { name: string; purpose: string; statusLabel: string };
  stages: Array<{ id: string; label: string; state: "complete" | "current" | "future" }>;
  currentQuestion: string;
  currentExperiment: { name: string; status: string; summary: string; notTestingYet: string[] };
  findings: Array<{ statement: string; status: "retained" | "rejected" | "provisional"; replacement?: string }>;
  blockers: Array<{ statement: string; severity: "critical" | "limitation" }>;
  nextAction: { title: string; detail?: string };
  recentResults: { scaleFitness: unknown[]; headlineLevels: unknown[]; tradeSignalGenerated: boolean };
  running: Array<{ name: string; status: string; purpose: string }>;
  workLinks: Array<{ label: string; href?: string; note?: string }>;
};
```

Long term:

- `market-structure-engine` owns research state, findings, experiment state, and engine outputs.
- MSOS consumes/presents a compact summary.
- Signal Capture owns normalized observations/capture health.
- Hummingbot owns execution later.

MSOS must not become a second canonical source of research conclusions after the repo split.

## Staleness rule

- Current question, experiment, findings, and next action come from one explicit project-state source.
- Do not duplicate those strings across components.
- Do not derive next action from live telemetry.
- Updating project state is part of experiment completion.
- If project state is older than the newest accepted witness/result, show a small `Research state may be stale` warning.

## Codex implementation handoff

### Goal
Reorganize the existing experimental Mission Control into the founder-facing Market Structure Engine dashboard described above without changing detector math, capture behavior, strategy logic, or execution behavior.

### Relevant code paths from PR #5411

- `apps/msos-web/src/app/operator/mission-control/page.tsx`
- `apps/msos-web/src/components/MultiScaleStructureProbe.tsx`
- `apps/msos-web/src/components/ProbeAutoRefresh.tsx`
- `apps/msos-web/src/data/operatingLoopProbe.ts`
- `apps/msos-web/src/lib/signalCaptureProbe.ts`

### Required behavior

- Page identity becomes MARKET STRUCTURE ENGINE.
- Primary hierarchy follows the exact page order above.
- Existing detailed live evidence remains available under Technical details.
- Introduce one explicit project-state object shaped for later movement to `market-structure-engine`.
- Keep the page read-only.

### Constraints / non-goals

- No detector math changes.
- No Signal Capture behavior changes.
- No automatic strategy decisions.
- No execution wiring.
- No production deployment.
- No repo-split implementation in this PR.
- Preserve the existing live staging evidence path.

### Acceptance criteria

1. Purpose, current stage, current question, retained learning, blockers, and next action are visible without opening Technical details.
2. The primary view requires no internal identifiers to understand it.
3. Active stage is `Validate detected levels`.
4. Current question asks whether persistent multi-scale levels contain useful information about what happens next.
5. Next action is validation of future price interaction around persistent levels.
6. `No critical blockers` is explicit unless fresh evidence changes that.
7. Default results show 5m POOR, 15m MARGINAL, 1h USABLE, 4h USABLE, 1d PROVISIONAL.
8. Default results say persistent structure was detected and no trade signal was generated.
9. Detailed telemetry remains accessible but secondary/collapsed.
10. Hummingbot is not presented as active current work.
11. Live staging evidence still renders.
12. No detector/capture/execution behavior changes are included.
13. Implementation PR includes screenshot or equivalent rendered UI evidence.
14. Implementation PR reports Coordination Status against this document and PR #5411.

### Ownership warning

PR #5411 already owns the current Mission Control code paths. Do not create a second implementation writer editing those same files concurrently. Prefer continuing implementation on #5411 or explicitly superseding it before a replacement implementation branch begins.

## Coordination status

**Agreement:** partial
**Compared:** control-plane SOP, PPE PR #5411, Mission Control source/state, capture PR #2, 2026-08-13 live witness
**Disagreement:** current dashboard next action still describes an already-completed inspection; research has advanced to level validation
**Evidence gap:** predictive usefulness of persistent levels remains unknown
**Ownership overlap:** current research presentation crosses Signal Capture and MSOS; repo split should make ownership explicit
**Risk if unresolved:** Mission Control becomes a stale implementation monitor rather than a trustworthy project briefing
**Recommended default:** one small founder-facing reorganization against this contract, preserving detailed evidence underneath
**Founder decision required:** no for this dashboard IA
