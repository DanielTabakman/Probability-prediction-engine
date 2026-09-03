# Market Structure V0 — Full Project Report

**Status:** V0 research cycle complete  
**Research conclusion:** **NOT VALIDATED / NO EDGE DEMONSTRATED**  
**Primary market:** NDAX SOL/CAD  
**Team research console:** https://staging.marketstructureos.com/market-structure  
**Primary evidence:** `DanielTabakman/market-structure-engine` Issue #15  
**Audience:** OCT / Poro / MSOS collaborators, researchers, builders, and anyone evaluating what the market-structure project is for.

---

## Executive summary

Market Structure V0 is the first complete research cycle for the market-structure system.

The broad question behind the project is:

> **Can we detect market structure across multiple scales that tells us something useful about what price does next?**

V0 tested one narrow version of that idea:

> **Do persistent price levels that appear across multiple time scales produce future reactions more often than matched control levels?**

We built a deterministic multi-scale detector, extracted it into a dedicated `market-structure-engine`, froze the detector and validation rules, built historical replay and forward-validation tooling, compared detector-selected levels against deterministic matched controls, ran both historical and prospective tests, preserved immutable evidence artifacts, and surfaced the result in the Market Structure Lab.

The primary untouched batch contained:

- **168 / 168** predeclared four-hour windows successfully analyzed.
- **41,761 / 41,761** historical observations usable.
- Detector levels: **24 reactions / 144 touches = 16.67%**.
- Matched controls: **26 reactions / 137 touches = 18.98%**.
- Detector minus control: **−2.31 percentage points**.
- Predeclared 95% block-bootstrap confidence interval: **−10.56 pp to +5.88 pp**.
- Formal frozen verdict: **INCONCLUSIVE**.

The correct operational interpretation is:

> **V0 did not demonstrate predictive value and does not advance to a Hummingbot strategy or backtest.**

`INCONCLUSIVE` does not mean “almost passed.” It means the frozen statistical rule cannot distinguish the detector from the control strongly enough to declare PASS or FAIL. The point estimate was actually slightly negative: the matched controls performed better in the primary sample.

That does **not** prove that support/resistance is false, that market structure is useless, or that no price-level strategy can work. It means one precisely defined V0 hypothesis did not earn promotion.

The larger success of V0 is the reusable research system it produced:

```text
question
  ↓
predeclared hypothesis
  ↓
market observations
  ↓
deterministic detector
  ↓
matched baseline
  ↓
historical / prospective validation
  ↓
reproducible evidence artifact
  ↓
human-readable decision
  ↓
only if validated → Hummingbot strategy/backtest
```

The project is therefore better understood as a **research and market-intelligence layer in front of Hummingbot**, not as a support/resistance bot.

---

# 1. Why this project exists

The end goal is not merely to draw lines on charts.

The system is intended to answer a sequence of increasingly demanding questions:

1. **What actually happened in the market?**
2. **What structure can we detect?**
3. **At which time scales is the data usable?**
4. **Does the structure contain forward information?**
5. **Can that information be expressed as a strategy?**
6. **Does the strategy survive realistic backtesting and costs?**
7. **Does it survive paper trading?**
8. **Only then, should anything trade live?**

The intended research-to-execution pipeline is:

```text
MARKET DATA
     ↓
Signal Capture / historical sources
"what actually happened?"
     ↓
MARKET-STRUCTURE ENGINE
"what structure do we see?"
     ↓
RESEARCH VALIDATION
"does that structure predict anything?"
     ↓
             NO → preserve result, reject/change hypothesis
             YES
              ↓
       STRATEGY RULE
              ↓
         HUMMINGBOT
   backtest → paper → gated live
              ↓
           RESULTS
              ↓
            learn
```

The separation is deliberate:

- A visually interesting pattern is **not** automatically a predictive signal.
- A predictive signal is **not** automatically a profitable strategy.
- A profitable backtest is **not** automatically robust live execution.

V0 exists to enforce the first gate before capital or execution becomes involved.

---

# 2. Why persistent multi-scale levels were the first hypothesis

The original intuition comes from the familiar support/resistance phenomenon: markets often appear to revisit, reject, consolidate around, or break through recurring price regions.

The research question was not “can a human draw convincing support/resistance lines?” Humans can almost always do that after seeing a chart.

The better question was:

> **Can recurring structure emerge algorithmically, before future price behavior is observed?**

A second design decision was equally important:

> **Do not choose one privileged timeframe first.**

Instead, V0 applies essentially the same relative structure logic across multiple horizons:

- 5 minutes
- 15 minutes
- 1 hour
- 4 hours
- 1 day

This allows three questions to remain separate:

```text
What structures exist?
      ↓
detect across scales

Which scales are actually measurable on this feed?
      ↓
feed fitness by scale

Which structures/scales contain predictive information?
      ↓
validate against future data and controls
```

That separation produced one of the strongest retained findings from V0: **data quality is scale-dependent**.

---

# 3. Retained finding: feed quality is scale-dependent

The first live NDAX SOL/CAD witness showed approximately:

```text
5m      POOR
15m     MARGINAL
1h      USABLE
4h      USABLE
1d      provisionally USABLE
```

The important interpretation is not “NDAX is bad data.”

It is:

> **The same market feed can be too noisy for fine-grained five-minute structure while remaining useful for one-hour or four-hour structure.**

For example, when the bid/ask spread is large relative to the entire five-minute price range, apparent five-minute structure can be dominated by microstructure noise. Over four hours, that same spread may be small relative to genuine market movement.

This means feed quality should be evaluated **relative to the scale of the question being asked**, rather than labelled globally good or bad.

This finding remains useful regardless of the V0 predictive result.

---

# 4. What the detector does

The V0 detector was extracted into its own repository:

- `DanielTabakman/market-structure-engine`

The extraction preserved the existing detector rather than silently rewriting it. A shadow-equivalence witness confirmed that the extracted engine produced the same scale fitness, zones, persistent levels, and semantic output as the original implementation.

Conceptually, the detector does this:

```text
normalized observations
       ↓
examine price behavior at several horizons
       ↓
identify recurring local interaction/turning areas
       ↓
cluster nearby observations into zones
       ↓
repeat across horizons
       ↓
find price regions that recur across horizons
       ↓
persistent multi-scale levels
```

In V0, a persistent level generally means that substantially the same price region appears on at least two scales.

This creates a more testable object than subjective chart annotation. Instead of saying “this looks like support,” we can say:

> “This price region independently emerged from the same detector at multiple horizons.”

That object can then be frozen at time T and evaluated against future data.

---

# 5. What V0 specifically hypothesized

The broad thesis is:

> Market structure may contain useful information.

V0 tested the much narrower proposition:

> **Persistent multi-scale levels should produce future price reactions more frequently than comparable control levels.**

This is intentionally narrow.

V0 did **not** test every possible interpretation of support/resistance or market structure. It tested one operational definition that could be written in code and evaluated without hindsight.

---

# 6. Frozen V0 event rules

The validator froze simple rules before the primary evaluation.

### Persistent level

A detected level that persists across at least two scales.

### Forward window

**4 hours** after detection time T.

### Touch

Future price comes within **10 basis points** of the frozen level.

### Reaction

After first touch, price moves at least **25 basis points away** from the level within **30 minutes**.

The resulting experiment is approximately:

```text
At time T:
- freeze the current detector output
- freeze the current price

During the next 4 hours:
- did price reach the level?
- if yes, did it move meaningfully away soon afterward?
```

These are V0 heuristics, not claims that 10 bps, 25 bps, 30 minutes, or 4 hours are universally optimal.

The point of V0 was to **freeze one coherent definition and test it**, not search parameter space until something looked good.

---

# 7. Why matched controls are essential

A reaction around a detected level is not sufficient evidence.

Markets move around constantly. A nearby arbitrary price may appear to generate a “reaction” simply because price frequently reverses or moves after touching anything.

Therefore V0 compared each detected level to a deterministic matched control.

The control is constructed by mirroring the detector level around the frozen current price.

Example:

```text
current price = 100

detector level = 95
(distance from current price = 5)

matched control = 105
(same distance from current price)
```

So the scientific comparison becomes:

```text
DETECTOR
prices our algorithm believes matter

versus

CONTROL
similarly located prices the algorithm did not select
```

The real question is therefore not:

> “Did price react near our detected levels?”

It is:

> **“Did price react near our detected levels more often than it reacted near comparable levels?”**

Without this control, V0 would have been much easier to fool ourselves with.

---

# 8. What V0 deliberately did not test

V0 is an **information validation experiment**, not a trading strategy.

It did not test:

- profitability;
- trading fees;
- slippage;
- position sizing;
- long/short entries;
- stop losses;
- support versus resistance directionality;
- breakout entries;
- LP profitability;
- market-making profitability;
- execution quality;
- portfolio construction;
- Hummingbot strategy performance.

The intended ladder is:

```text
Does the feature contain forward information?
              ↓ YES
Can we define a strategy around it?
              ↓
Does the strategy survive Hummingbot backtesting?
              ↓
Does it survive paper trading?
              ↓
Does tiny live execution behave as expected?
```

V0 stopped at the first gate because it did not earn the next step.

---

# 9. Evidence sequence

V0 was not one giant backtest. It developed through several evidence stages.

## 9.1 Initial historical pilot — July 15–18, 2026

The first historical replay used a small SOL/CAD sample.

Results:

```text
12 / 12 windows usable

Detector:
1 reaction / 10 touches
= 10.0%

Controls:
2 reactions / 11 touches
= 18.18%
```

Every individual four-hour window was formally inconclusive because each window contained too few qualifying touches.

This pilot taught us something methodological:

> **Single four-hour experiments are sparse for this detector.**

It did not justify changing detector thresholds after seeing the result.

Instead, it justified accumulating more predeclared observations.

---

## 9.2 Prospective holdout — August 15, 2026

We also ran a genuine prospective test.

The detection time and experiment rules were frozen before the future four-hour window completed.

That prevents accidental hindsight selection.

The holdout produced:

```text
Detector:
0 touches
0 reactions

Controls:
0 touches
0 reactions
```

Formal result:

**INCONCLUSIVE**

This was useful because it reinforced the sample-density finding: a single clean four-hour holdout can easily produce no relevant events at all.

---

## 9.3 June expansion attempt — data unavailable

We then predeclared a much larger June sample.

NDAX historical retention proved incomplete for the requested period. Only **36 / 180** planned anchors had usable data.

The experiment stopped under the predeclared data-quality rule.

Classification:

**DATA_INCOMPLETE**

The partial subset was **not** used as a scientific conclusion.

This distinction matters:

```text
bad / missing data
≠
bad detector
≠
bad hypothesis
```

A research system should be able to separate those outcomes.

---

# 10. Primary V0 test — July 18 through August 14, 2026

The final primary sample was predeclared over a recent period with complete NDAX historical coverage.

Coverage:

```text
168 predeclared 4-hour windows
168 / 168 successfully analyzed

41,761 historical observations
41,761 usable
0 rejected
```

This sample crossed the predeclared minimum evidence gate of at least 30 touched levels in each arm.

## Detector arm

```text
144 touches
24 reactions

reaction rate given touch:
16.67%
```

## Matched-control arm

```text
137 touches
26 reactions

reaction rate given touch:
18.98%
```

## Point estimate

```text
Detector − Control

16.67% − 18.98%
= −2.31 percentage points
```

The raw estimate therefore leaned slightly **against** the V0 detector.

---

# 11. Statistical inference

Adjacent market events are not independent coin flips. Market regimes and volatility persist through time.

To avoid pretending each touch was independent, V0.1 used a **four-hour-anchor block bootstrap**.

Predeclared parameters:

- 10,000 bootstrap replicates
- fixed seed `20260816`
- resampling unit: four-hour experimental anchors

Result:

```text
Point difference:
−2.31 percentage points

95% confidence interval:
−10.56 pp to +5.88 pp
```

The interval crosses zero.

Under the frozen rule:

- PASS only if the full interval is above zero.
- FAIL only if the full interval is below zero.
- Otherwise: INCONCLUSIVE.

Therefore the formal result is:

> **INCONCLUSIVE**

---

# 12. What “INCONCLUSIVE” means here

It does **not** mean:

> “V0 almost worked.”

It means:

> **The observed evidence does not let us distinguish the detector from the matched control strongly enough to declare a positive or negative effect under the frozen statistical rule.**

The point estimate was:

```text
Detector: 16.67%
Control:  18.98%
```

So the observed central estimate was not promising.

At the same time, the confidence interval is wide enough that the underlying effect could still be modestly positive or materially negative.

The correct pair of statements is therefore:

### Scientific statement

**V0 has not established predictive value.**

### Operational statement

**Do not promote V0 to a strategy or Hummingbot backtest.**

This is stronger and more useful than simply displaying the word `INCONCLUSIVE`.

---

# 13. What V0 does not prove

V0 does **not** prove any of the following:

- support and resistance does not exist;
- all price levels are meaningless;
- multi-scale analysis is wrong;
- market structure is useless;
- breakout strategies cannot work;
- directional support/resistance cannot work;
- regime-conditioned structure cannot work;
- no profitable strategy can use market structure.

V0 tested one precise proposition:

> **The current persistent multi-scale detector, evaluated with the current touch/reaction definition, should beat matched controls.**

That proposition did not validate.

---

# 14. Why V0 is still a successful research project

If the purpose of V0 had been “prove support/resistance works,” then it would be a failed project.

That is the wrong objective.

The correct objective is:

> **Build a system capable of deciding whether a market idea deserves further engineering and capital.**

By that standard, V0 succeeded.

It prevented this sequence:

```text
interesting chart pattern
        ↓
looks convincing
        ↓
build strategy
        ↓
search parameters until backtest looks good
        ↓
risk money
```

and replaced it with:

```text
interesting market idea
        ↓
precise hypothesis
        ↓
frozen detector + baseline
        ↓
untouched evaluation
        ↓
no demonstrated edge
        ↓
STOP
```

The ability to say “do not trade this yet” is one of the most valuable outputs a trading-research system can produce.

---

# 15. The reusable product created by V0

V0 started as a support/resistance-style research experiment.

The reusable system that emerged is broader:

```text
QUESTION
    ↓
HYPOTHESIS
    ↓
DETERMINISTIC TEST
    ↓
MARKET DATA
    ↓
MATCHED BASELINE
    ↓
RESULT
    ↓
IMMUTABLE EVIDENCE
    ↓
HUMAN CONCLUSION
    ↓
NEXT DECISION
```

Only validated information proceeds to:

```text
VALIDATED INFORMATION
        ↓
STRATEGY EXPRESSION
        ↓
HUMMINGBOT BACKTEST
        ↓
PAPER
        ↓
GATED LIVE
```

The useful product framing is therefore something like:

> **A market-intelligence and research layer in front of Hummingbot.**

Hummingbot supplies generic trading infrastructure.

Our differentiated layer asks:

- what market state appears to exist;
- what hypotheses are worth testing;
- whether those hypotheses survive explicit baselines;
- whether a research idea has earned the right to become a strategy.

---

# 16. Current architecture

```text
                 MARKET
                   │
                   ▼
          ┌──────────────────┐
          │  Signal Capture  │
          │ specialist data  │
          └────────┬─────────┘
                   │
                   │ normalized observations
                   ▼
       ┌───────────────────────────┐
       │ Market Structure Engine   │
       │                           │
       │ feed fitness              │
       │ structure detection       │
       │ cross-scale persistence   │
       │ experiments               │
       │ validation                │
       └─────────────┬─────────────┘
                     │
                     │ structured evidence
                     ▼
             ┌──────────────┐
             │     MSOS     │
             │ Research Lab │
             │ / dashboard  │
             └──────┬───────┘
                    │
        validated idea only
                    │
                    ▼
             ┌──────────────┐
             │  Hummingbot  │
             │              │
             │ backtesting  │
             │ paper        │
             │ execution    │
             └──────────────┘
```

The boundaries are intentional.

---

# 17. Signal Capture's role

Signal Capture owns specialist observation infrastructure:

- collection;
- normalization;
- persistence;
- timestamps/provenance;
- capture health;
- high-resolution research evidence where generic sources are insufficient.

It is **not** intended to become another execution platform.

During V0, one operational issue demonstrated why this separation matters: active gzip index files could remain unreadable to downstream readers even while capture was actively writing.

The fix finalized the current gzip member on every periodic flush and appended a new member on subsequent writes. This kept the same logical gzip stream and schema while allowing downstream research to remain close to wall-clock freshness.

That was a data-pipeline problem, not a detector or hypothesis problem.

---

# 18. Market Structure Engine's role

The Market Structure Engine is the deterministic scientific core.

It owns:

- feed fitness by scale;
- structure-zone detection;
- cross-scale persistence;
- historical replay;
- frozen experiments;
- control construction;
- validation metrics;
- experiment persistence;
- machine-readable evidence.

It deliberately does **not** own:

- wallets;
- exchange credentials;
- order placement;
- fills;
- live execution;
- product/UI state;
- human conclusions.

That keeps research math separable from agents and execution systems.

An agent may reason about experiment output, but it should not silently alter the detector while deciding whether the detector works.

---

# 19. MSOS / Market Structure Lab's role

MSOS is the human-facing research and workflow layer.

Current staging page:

https://staging.marketstructureos.com/market-structure

The most important UI distinction is:

## LIVE MARKET

> What does the detector see right now?

versus

## RESEARCH EVIDENCE

> Do we have evidence that what the detector sees is predictive?

Those must remain separate.

A live market screen may show usable scales and candidate persistent levels while the research status simultaneously says:

```text
V0
NOT VALIDATED
NO EDGE DEMONSTRATED
```

That is not a contradiction.

It means:

> **Detection is not validation.**

The current V0 lifecycle is therefore:

```text
Detect      ✓ complete
Validate    ✓ complete
Strategy    BLOCKED
Backtest    BLOCKED
Trade       BLOCKED
```

The V0 dashboard intentionally removed the ability to repeatedly rerun the completed prospective test from the UI. The result should be preserved, not rerun until something passes.

---

# 20. What the ZIP evidence artifact is

Each serious batch produces a machine-readable evidence artifact.

Primary V0 artifact:

- name: `untouched-jul18-aug14-batch-v0.1`
- GitHub Actions artifact ID: `9258661760`
- ZIP SHA-256: `8b7168bd485a852bdc2a6f9d345a93800eb153415e751de37594aefe5dc91b00`

The ZIP is **not** the product experience.

It is the experiment's sealed lab notebook.

It contains the information needed to audit/reproduce the result, including:

- source provenance;
- row coverage;
- detector/version identity;
- evaluation parameters;
- all predeclared anchors;
- detector levels;
- matched control levels;
- touches;
- reactions;
- individual outcomes;
- pooled counts;
- bootstrap procedure;
- final verdict.

The dashboard therefore presents:

```text
human-readable result
        ↓
Evidence & reproducibility
        ↓
GitHub witness
raw ZIP / JSON
artifact hash
```

A teammate should never need to open the ZIP to understand the conclusion.

But anyone should be able to open it to audit the conclusion.

---

# 21. Why reproducibility matters

Agent-assisted quantitative research becomes dangerous if the reasoning trail disappears.

A bad future explanation would be:

> “An agent tested this and I think it didn't work.”

The desired evidence chain is:

```text
hypothesis version
↓
exact detector
↓
exact observations
↓
predeclared evaluation windows
↓
matched controls
↓
raw outcomes
↓
fixed statistical procedure
↓
immutable artifact
↓
human decision
```

That turns agent-assisted analysis into an **auditable research process** rather than an opaque recommendation engine.

---

# 22. What V0 remains useful for

The predictive hypothesis did not validate, but several V0 capabilities remain valuable.

## A. Multi-scale feed fitness

The engine can answer:

> Which horizons are actually observable on this market/feed?

That is useful for almost any later strategy research.

## B. Deterministic structure description

The engine can still describe recurring interaction zones.

That can be useful for:

- human market context;
- dashboard annotations;
- generating future research hypotheses;
- conditioning variables in later experiments.

Those structures must remain labelled **descriptive / candidate**, not validated signals.

## C. Historical research infrastructure

V0 established working infrastructure for:

- NDAX historical ingestion;
- inside bid/ask normalization;
- isolated historical datasets;
- replay without future leakage;
- deterministic controls;
- batch inference;
- experiment artifacts;
- authenticated research APIs;
- human-facing evidence summaries.

That work is reusable across future hypotheses.

## D. A gate in front of Hummingbot

Instead of:

```text
trading idea
↓
Hummingbot
```

we now have:

```text
trading idea
↓
research evidence
↓
validated?
   ↓
NO → stop
YES → strategy definition
      ↓
      Hummingbot
```

That is a valuable control against wasted engineering, overfitting, and premature execution.

---

# 23. Scientific lessons retained from V0

## 1. Market structure can be detected algorithmically

Recurring zones were not purely subjective drawings.

## 2. Similar structures appear across scales

The multi-scale descriptive framework is viable.

## 3. Feed usefulness is scale-dependent

A single venue/feed should not be labelled globally “good” or “bad.”

## 4. Recurrence does not automatically imply predictive value

Something can be visually real, algorithmically detectable, persistent, and multi-scale while still failing to beat a simple baseline.

## 5. Controls are essential

Without matched controls, V0 would have looked more impressive than it actually was.

## 6. Sparse events require batch-level inference

Single four-hour windows rarely contained enough qualifying touches to be decisive.

## 7. Data failures must be separated from research failures

The incomplete June sample was treated as a data limitation, not evidence against the hypothesis.

## 8. Negative results are valid product output

“Do not build this strategy” is a useful research conclusion.

---

# 24. Why V0 is frozen now

After observing the primary result, we should **not** respond by adjusting parameters until a positive result appears.

Examples of tempting post-result changes would be:

- touch = 15 bps instead of 10;
- reaction = 20 bps instead of 25;
- different forward window;
- require three scales instead of two;
- select only the best-looking time horizon.

Those may be reasonable future ideas, but once the evaluation result has been seen they cannot be treated as the same untouched hypothesis.

Repeatedly changing the detector while watching the evaluation sample is classic overfitting.

Therefore:

> **V0 stays frozen and preserved as tested.**

Any continuation becomes a separately written **V1** hypothesis with new evaluation data.

---

# 25. Where the project goes from here

There are two legitimate paths.

## Option A — stop research here for now

This is a valid outcome.

We learned that V0 does not justify a strategy, and the reusable research infrastructure remains available for the next genuinely important question.

There is no requirement to invent V1 immediately.

## Option B — begin a new V1 research cycle

If the team chooses to continue, V1 should use V0's failure as information about **which question to ask next**, not as an invitation to tune V0.

Several distinct hypotheses are plausible.

---

# 26. Possible V1: level strength as a continuous variable

V0 collapses a rich structure into a fairly binary property:

```text
persistent / not persistent
```

But perhaps the useful information is continuous.

Example:

```text
Level A
2 scales
3 prior interactions

Level B
3 scales
9 prior interactions

Level C
4 scales
18 prior interactions
```

A new hypothesis could be:

> **Does reaction probability or reaction magnitude increase with measurable level strength?**

This is genuinely different from simply changing the V0 persistence threshold.

---

# 27. Possible V1: directional support/resistance

V0 deliberately treated reaction as non-directional:

> touch → move away.

Traditional support/resistance implies direction:

```text
approach from above
↓
support behavior

approach from below
↓
resistance behavior
```

A new hypothesis could condition on:

- approach direction;
- recent trend;
- prior side of the level;
- previous breakout/reclaim behavior.

That is a separate research question.

---

# 28. Possible V1: breakout continuation rather than bounce

Perhaps persistent levels are not useful because price bounces from them.

Maybe the useful event is what happens **after a decisive break**.

A distinct hypothesis could be:

```text
persistent multi-scale level
      ↓
clean break
      ↓
confirmation
      ↓
retest / failure to reclaim
      ↓
future continuation
```

This connects directly to breakout/retest trading logic without pretending the V0 bounce hypothesis succeeded.

---

# 29. Possible V1: regime-conditioned structure

V0 asks whether the detector works approximately **on average**.

But structural effects may exist only under particular market conditions.

For example, persistent levels may behave differently during:

- low-volatility ranges;
- strong trends;
- volatility expansion;
- high-liquidity conditions;
- thin-liquidity conditions;
- favorable versus unfavorable spread/range ratios.

Then this quantity:

```text
P(reaction | persistent level)
```

may show little effect, while a conditional version might behave differently:

```text
P(reaction |
  persistent level
  AND range regime
  AND usable liquidity)
```

That would be a proper newly predeclared hypothesis.

---

# 30. The longer-term product direction

The eventual product does not need one universal “market structure signal.”

It could maintain a library of market-state hypotheses with explicit validation status:

```text
MARKET RESEARCH LIBRARY

Feed fitness by scale              retained finding
Persistent levels v0               not validated
Level-strength gradient             candidate v1
Directional support/resistance      candidate
Breakout continuation               candidate
Range regime                        future
Trend regime                        future
Volatility expansion                future
Liquidity regime                    future
Cross-venue dislocation             future
LP suitability                      future
```

MSOS can then become a market-intelligence layer that tells humans and downstream systems:

1. what the market currently looks like;
2. which observations are merely descriptive;
3. which features have actually survived validation;
4. which strategies are eligible for backtesting or execution.

That is a much stronger product than “a support/resistance bot.”

---

# 31. Relationship to Hummingbot

Hummingbot remains downstream generic trading infrastructure.

It should be reused for things such as:

- exchange connectivity;
- order management;
- fills;
- strategy execution;
- backtesting where supported;
- paper trading;
- Gateway / DEX interaction.

The market-structure project should focus its differentiated effort on:

```text
market understanding
+
research hypotheses
+
evidence
+
strategy eligibility
```

For V0 specifically:

```text
Detect        COMPLETE
Validate      COMPLETE
Strategy      BLOCKED
Hummingbot    BLOCKED
Trade         BLOCKED

Reason:
NO EDGE DEMONSTRATED
```

That is the architecture functioning correctly.

---

# 32. Current project state

```text
DATA PIPELINE
✅ working

FRESH LIVE NDAX OBSERVATIONS
✅ working

MULTI-SCALE DETECTOR
✅ working

ENGINE EXTRACTION
✅ shadow-equivalent

market-structure.v1
✅ working

HISTORICAL NDAX REPLAY
✅ working

FORWARD VALIDATION
✅ working

MATCHED CONTROLS
✅ working

PROSPECTIVE HOLDOUT
✅ working

BATCH STATISTICAL TEST
✅ working

IMMUTABLE EVIDENCE ARTIFACTS
✅ working

PUBLIC AUTHENTICATED RESEARCH API
✅ working

MARKET STRUCTURE LAB
✅ staging / team-facing

V0 PREDICTIVE EDGE
❌ not demonstrated

V0 STRATEGY
⛔ blocked

HUMMINGBOT BACKTEST FOR V0
⛔ not justified

LIVE TRADING
⛔ not attempted
```

---

# 33. Repositories and references

## Market Structure Engine

Repository: https://github.com/DanielTabakman/market-structure-engine

Important references:

- Detector extraction / `market-structure.v1`: https://github.com/DanielTabakman/market-structure-engine/pull/2
- Frozen forward validation v0: https://github.com/DanielTabakman/market-structure-engine/pull/10
- Historical replay + batch validation v0.1: https://github.com/DanielTabakman/market-structure-engine/pull/13
- Primary complete V0 evidence: https://github.com/DanielTabakman/market-structure-engine/issues/15
- Canonical V0 conclusion state: https://github.com/DanielTabakman/market-structure-engine/pull/16

## Signal Capture

Repository: https://github.com/DanielTabakman/poroburu-oct-signal-capture

Relevant persistence/freshness fix:

- https://github.com/DanielTabakman/poroburu-oct-signal-capture/pull/5

## MSOS / Probability Prediction Engine

Repository: https://github.com/DanielTabakman/Probability-prediction-engine

Market Structure Lab / control panel work:

- https://github.com/DanielTabakman/Probability-prediction-engine/pull/5411

Team staging page:

- https://staging.marketstructureos.com/market-structure

Primary evidence artifact:

- name: `untouched-jul18-aug14-batch-v0.1`
- artifact ID: `9258661760`
- SHA-256: `8b7168bd485a852bdc2a6f9d345a93800eb153415e751de37594aefe5dc91b00`

---

# 34. Two-minute explanation for a teammate

> **We are building a research layer in front of Hummingbot.**
>
> Our first test was whether recurring price levels that appear across multiple timeframes actually predict future price reactions.
>
> We built a deterministic detector, froze it, compared its detected levels against matched control levels, and tested it on both historical and prospective data.
>
> The final untouched test contained 168 four-hour windows and enough level interactions to evaluate the hypothesis properly.
>
> Our detected levels reacted 16.7% of the time after touch. Controls reacted 19.0% of the time. The difference was −2.3 percentage points, and the statistical interval crossed zero.
>
> Therefore **V0 did not demonstrate an edge**. We are not turning it into a Hummingbot strategy.
>
> The valuable outcome is that the research machinery now works end to end: market data → structure detection → controls → historical/prospective validation → reproducible evidence → dashboard → strategy only if validated.
>
> The live dashboard still displays market structure, but it explicitly separates **“we detect this”** from **“we have evidence this predicts anything.”**
>
> If we continue, we will create a genuinely new V1 hypothesis before examining its evaluation data rather than tuning V0 until it passes.

---

# 35. One-sentence description

> **Market Structure V0 built and proved out an auditable research pipeline for testing market structure before handing ideas to Hummingbot; its first hypothesis—persistent multi-scale price levels predict reactions better than matched controls—did not validate, so the hypothesis stops while the research system survives.**
