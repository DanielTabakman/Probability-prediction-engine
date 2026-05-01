---
title: "PPE Master (MVP1 controlling canon)"
source: "Imported from `d:/Users/User/Downloads/PPE Master — Vision, Canon, Build Order, and Current Audit.md`"
imported_utc: "2026-04-30"
control_rule: "For MVP1 implementation, MVP1-specific sections override broad canon if they appear to conflict."
---

PPE Master — Operating Architecture, Canon, MVP1, and Current Audit

AI-first navigation layer  
This document is the single master control document for PPE.  
It is structured primarily for AI implementation and steering use.  
Human readability matters, but AI interpretability takes precedence.

How this document is meant to work  
This document supports a two-way workflow:  
\- top-down: vision \-\> strategy \-\> product goal \-\> roadmap \-\> phase contract \-\> implementation  
\- bottom-up: implementation \-\> validation \-\> feedback/evidence \-\> review \-\> audit \-\> explicit corrections upward

Conflict-resolution rule  
If a broad canon section and an MVP1-specific section appear to disagree, the MVP1-specific section controls MVP1 implementation.  
Do not let broad canon language silently widen MVP1 scope.

Bottom-up correction rule  
Bottom-up evidence is allowed to challenge:  
\- current audit judgments  
\- threshold proxies  
\- sequencing assumptions  
\- implementation details

Bottom-up evidence is not allowed to silently rewrite:  
\- project identity  
\- fixed MVP1 scope  
\- no-trade as a first-class output  
\- benchmark contract  
\- review contract  
\- out-of-scope boundaries

Approved update rule  
If bottom-up evidence reveals a real mismatch, the correction should be written back into this document explicitly rather than silently absorbed into code behavior.

AI reading order  
For an implementation agent, the recommended reading order is:  
1\. Section 1 — Strategic stack  
2\. Section 5 — PPE canon  
3\. Section 6 — Wedge 1: ATM width disagreement  
4\. Section 7 — Output states  
5\. Section 12 — Current audit  
6\. Section 13 — MVP1 and phase architecture  
7\. Section 14 — Product governance contract  
8\. Section 15 — MVP1 product behavior contract

Why this reading order  
It gives the agent:  
\- the project’s purpose first  
\- the reusable system logic second  
\- the active wedge third  
\- the current-state placement fourth  
\- the fixed MVP contract fifth  
\- the exact behavior contract sixth

Canonical summary  
The code should flow downward from the controlling contract.  
Corrections should flow upward from evidence.  
Neither direction should bypass the document.

Purpose  
This is the single master document for PPE.  
Its job is to keep the project coherent while it is still being built, reduce term drift, preserve the project’s logic, identify the current bottleneck, and make future build choices easier.

This is not a marketing document.  
This is not a hype deck.  
This is a working operating architecture.

\============================================================  
1\. STRATEGIC STACK  
\============================================================

Vision  
Why the product exists.  
PPE exists to help turn opaque market structure into legible, auditable, and eventually evidence-backed research judgments that a human can inspect, challenge, and learn from.

Strategy / Theory of Change  
How the product creates change.  
PPE creates change by:  
1\. making market structure legible,  
2\. surfacing candidate disagreements relative to an explicit benchmark,  
3\. filtering those disagreements for trust and materiality,  
4\. mapping them into cautious expression families or valid no-trade outputs,  
5\. freezing what it said before the outcome,  
6\. reviewing what happened later,  
7\. promoting only those classes that survive repeated evidence.

Current Product Goal  
The major outcome currently being pursued.  
Build the first honest closed-loop MVP for one BTC options disagreement class: ATM width disagreement, with freeze-and-review built into the loop.

Success Metrics  
How progress is judged.  
Use two clocks.

Engineering clock  
Tracks product and implementation progress.  
Examples:  
\- dashboard legibility preserved  
\- benchmark explicitly visible  
\- deterministic classification under fixed inputs  
\- no-trade behaves correctly  
\- frozen evaluations persist and reopen  
\- review statuses are finite and explicit

Evidence clock  
Tracks whether the system is becoming a real research engine.  
Examples:  
\- count of frozen evaluations  
\- count of reviewed cases  
\- percent of cases clean enough to teach from  
\- separation quality across trust/confidence buckets  
\- class-level continue/refine/suppress/retire verdicts becoming meaningful

Canonical rule  
A clean slice can move the engineering frontier.  
It does not automatically move the evidence frontier.

Roadmap  
The sequence of major product movements.

Roadmap chapter 1  
Create the first narrow closed loop:  
\- benchmarked evaluation  
\- candidate/watch/no-trade output  
\- frozen snapshot  
\- later review  
\- class summary

Roadmap chapter 2  
Strengthen the loop:  
\- better benchmark formalization  
\- stronger materiality logic  
\- better review density  
\- stronger execution realism

Roadmap chapter 3  
Expand breadth carefully:  
\- more anomaly subtypes  
\- richer expression logic  
\- stronger class-level learning  
\- controlled first-dollar protocol tests

Roadmap chapter 4  
Only later:  
\- broader anomaly coverage  
\- richer implementation detail  
\- deeper automation  
\- stronger operationalization

\============================================================  
2\. WORK HIERARCHY  
\============================================================

Phase  
A bounded chapter of the roadmap.  
A phase should unlock a meaningful new capability boundary.

Epic / Initiative  
A cluster of related product changes inside a phase.  
Epics are larger than slices and should still preserve one coherent product theme.

Slice / Ticket  
The smallest meaningful coherent change.  
A slice should change the product in one bounded way that can be validated and closed.

Task / Subtask  
The concrete implementation steps needed to complete a slice.  
Tasks are execution details, not product-level decisions.

Canonical rule  
Product decisions should generally be made no lower than the phase or epic level.  
Slices and tasks should execute the product contract, not invent it.

\============================================================  
3\. LIFECYCLE / CONTROL LOOP  
\============================================================

Selection  
The next work unit is chosen.

Spec / Clarification  
The contract for the selected work is made explicit enough to implement without guessing.

Build  
The change is implemented.

Validation  
Tests, checks, and evidence confirm whether the change behaves as intended.

Closeout  
The change is integrated back into steering truth with evidence and updated understanding.

Release / Operationalization  
The change reaches actual operator use, live workflow use, or product-visible use.  
For PPE, this does not always mean public release.

Feedback / Evidence  
Observed behavior, reviewed outcomes, and validation evidence inform the next selection and may also update the current audit or broader product understanding.

Canonical rule  
Work type and work state are different dimensions.  
A slice is a type of work item.  
Selection \-\> Build \-\> Validation \-\> Closeout is the lifecycle of that work item.

\============================================================  
4\. ARTIFACT LAYER  
\============================================================

PR / Commit  
The code artifact.

Validation Evidence  
The proof that the change works.  
Examples: unit tests, smoke tests, screenshots, structured review examples, logs.

Release / Operationalization Artifact  
The visible or usable behavior change.  
Examples: new UI surface, stored record, review screen, class summary table.

Feedback Artifact  
The evidence that informs future steering.  
Examples: operator notes, frozen cases, reviewed cases, class-level summary changes, audit updates.

Canonical rule  
Artifacts prove that work happened.  
They are not the same thing as the product decisions that justified the work.

\============================================================  
5\. PPE CANON  
\============================================================

Project identity  
Probability Prediction Engine (PPE)

Aspirational naming rule  
The name PPE is allowed to be aspirational.  
It names the direction of travel, not a claim that the current system has already reached full probability-engine maturity.

Canonical rule  
PPE may keep an aspirational identity at the project level while maintaining strict honesty at the output level.

Current-stage description  
PPE is currently best understood as a human-centered BTC volatility / relative-value research cockpit that is trying to become an auditable edge-research system.

Core product thesis  
PPE should help the operator:  
\- see what the market is implying  
\- identify legible disagreements worth inspection  
\- filter those disagreements for trust and materiality  
\- map them into expression families  
\- remember what was flagged before the outcome  
\- review what happened and learn which classes deserve promotion

What PPE is  
\- a BTC-first decision-support and edge-research system  
\- a market legibility and candidate-triage cockpit  
\- a human-in-the-loop research machine  
\- a project that should evolve from instrument panel \-\> candidate engine \-\> learning system

What PPE is not  
- not a guarantee of mispricing  
- not a promise of profit  
- not a substitute for risk management  
- not yet an autonomous trading engine  
- not yet a full probability engine in the strong evidence-backed sense

The most important ladder  
Pattern \-\> Disagreement \-\> Candidate Anomaly \-\> Candidate Signal \-\> Paper-Tracked Setup \-\> Acted Setup \-\> Evidence-Backed Edge

Definitions  
- Pattern: something visible in the market representation.  
- Disagreement: a meaningful difference between market structure and a chosen reference.  
- Candidate anomaly: a disagreement that looks unusual enough to inspect.  
- Candidate signal: a candidate anomaly that survives initial filtering and seems worth attention.  
- Paper-tracked setup: a candidate that has been frozen before outcome under explicit review rules.  
- Acted setup: a setup that is actually implemented under bounded rules.  
- Evidence-backed edge: a class of setups that shows repeatable positive expected value after costs, uncertainty, and review.

Canonical warning  
Pattern is not edge.  
Interesting is not tradable.  
Tradable is not profitable.  
Profitable once is not evidence-backed.

Canonical operating sequence  
See \-\> Compare \-\> Detect \-\> Filter \-\> Express \-\> Control \-\> Learn

In longer form  
1\. Represent the market honestly.  
2\. Compare it to a reference.  
3\. Detect candidate disagreements.  
4\. Filter for trust and materiality.  
5\. Map the surviving view to an expression family.  
6\. Decide whether to watch, paper-track, act, or output no-trade.  
7\. Review the outcome and update the system.

The 7-layer PPE stack

Layer 1: Sensing  
Question: What is the market saying?  
Goal: make the market legible.  
Examples: spot, chain, ATM IV, skew, term structure, implied distribution, trust indicators.  
Failure mode: reasoning on top of unstable market representation.

Layer 2: Reference  
Question: Relative to what should the market be judged?  
Goal: create the benchmark that makes disagreement measurable.  
Examples: baseline model, internal consistency constraints, historical behavior, realized-vs-implied relationships, saved belief curve.  
Failure mode: vague anomaly language with no explicit benchmark.

Layer 3: Detection  
Question: What looks off?  
Goal: produce candidate anomalies to inspect.  
Examples: market too wide, market too narrow, peak shift, skew distortion, term inconsistency.  
Failure mode: confusing raw patterns with meaningful candidate signals.

Layer 4: Filtering  
Question: Which candidates are trustworthy and material enough to matter?  
Goal: reduce false positives and prevent dashboard theater.  
Examples: data quality checks, stale quote checks, liquidity filters, materiality thresholds, confidence logic, artifact warnings.  
Failure mode: persuasive noise.

Layer 5: Expression  
Question: How would this view be expressed?  
Goal: map interpretation into structured payoff families.  
Examples: long vol family, short vol family, spreads, directional convexity, calendars, skew expressions.  
Failure mode: jumping to exact-ticket precision too early.

Layer 6: Control  
Question: Should this be acted on, and under what rules?  
Goal: protect capital and preserve attribution integrity.  
Examples: paper-track first, no-trade conditions, size caps, concentration limits, max loss bounds, go / no-go rules.  
Failure mode: acting too early and learning the wrong lesson.

Layer 7: Learning  
Question: Did the system actually generate value?  
Goal: turn PPE from a dashboard into a research engine.  
Examples: candidate logging, paper-tracking, fixed review horizons, calibration, false-positive review, class-level EV tracking.  
Failure mode: operating on vibes and memory instead of tracked evidence.

Canonical design principles  
1\. Legibility first.  
2\. Benchmark before judgment.  
3\. Prefer narrow wedges early.  
4\. Do not let naming outrun evidence.  
5\. Explanation quality matters.  
6\. Preserve dashboard visibility.  
7\. Keep action grammar above exact trade picking.  
8\. Track before claiming.  
9\. Separate research truth from marketing truth.  
10\. Protect closure quality.

High-value glossary

Market structure  
The visible shape and relationships present in options and related market data.  
Industry-near: implied vol surface, skew, smile, term structure, cross-strike and cross-expiry relationships, implied distribution.

Reference model  
The benchmark used to judge whether the market looks off.  
Industry-near: fair-value model, baseline model, statistical reference, no-arbitrage frame, internal consistency benchmark.

Candidate edge  
A candidate signal that may represent positive expected value if the logic is sound and the setup is real.  
Not the same as evidence-backed edge.

Mispricing  
Use carefully.  
In strict terms, mispricing means the market is wrong enough relative to a defensible model to create positive expected value after costs, uncertainty, and execution reality.  
Rule: do not casually use mispricing as a synonym for disagreement.  
Preferred early-stage language: candidate anomaly, candidate disagreement, candidate edge, mispricing candidate.

Confidence  
Confidence should mean confidence in candidate quality and trustworthiness, not certainty of profit.

Falsification condition  
What would make the candidate thesis stop being worth believing.  
This can include logical failure conditions, not only stop-loss style rules.

\============================================================  
6\. WEDGE 1 — ATM WIDTH DISAGREEMENT  
\============================================================

Current first wedge  
Width disagreement remains the correct first wedge.

Why this wedge first  
- closest to current product language  
- easiest to make legible  
- easiest to explain  
- easiest to map into expression families  
- lowest conceptual jump from the current state

Canonical v1 candidate definition  
A v1 candidate is a legible mismatch between market-implied structure and a chosen reference model or belief, large enough to matter, explainable in plain language, and clean enough to survive basic trust checks.

Canonical v1 filter  
A v1 candidate must pass all of:  
1\. a mismatch exists  
2\. the mismatch is material  
3\. the mismatch is legible  
4\. the mismatch survives trust checks  
5\. the mismatch maps to an expression family or a valid no-trade output

Width disagreement must be formalized  
Width disagreement can no longer remain only intuitive or visual.

Minimum formalization requirements  
Each width-disagreement candidate should eventually specify:  
- which horizon is being judged  
- which venue or data source defines the market input  
- which strike region or convention is being used  
- which reference the width is being judged against  
- whether the disagreement is ATM width, term width, event-adjusted width, or another named subtype  
- whether the signal is broad, local, or mixed  
- whether data quality is high enough to trust the width estimate

Immediate internal subtype split  
Even if product UI still treats width disagreement as one wedge, internally PPE should distinguish at least:  
- ATM width disagreement  
- term width disagreement  
- event-adjusted width disagreement

Canonical warning  
"Market too wide" is not yet the same as "short vol."  
"Market too narrow" is not yet the same as "long vol."  
Width only becomes economically meaningful after benchmark quality, execution realism, and repeated review are strong enough.

Materiality for width disagreement  
The size of the disagreement matters because PPE is not trying to notice every difference.  
It is trying to notice differences that are large enough to survive noise, model uncertainty, and basic execution reality.

Canonical rule  
A disagreement is only economically meaningful when it clears the relevant floor of indifference.

Why size matters  
If the gap is too small, then one or more of the following is true:  
- it may be within measurement noise  
- it may be within benchmark uncertainty  
- it may disappear inside conservative friction assumptions  
- it may not teach the system anything useful even if it looks interesting

System-based materiality framework  
For MVP1, materiality should be treated as a relationship, not just a raw threshold.

Define:  
- market width \= W\_m  
- benchmark width \= W\_b  
- absolute gap \= G\_abs \= |W\_m \- W\_b|  
- relative gap \= G\_rel \= |W\_m \- W\_b| / max(|W\_b|, epsilon)

The system should compare the gap to a materiality floor, not to a naked arbitrary number.

Define the materiality floor as:  
M\_floor \= max(N\_measurement, N\_benchmark, N\_execution)

Where:  
- N\_measurement \= uncertainty in the market-width estimate  
- N\_benchmark \= uncertainty in the benchmark-width estimate  
- N\_execution \= minimum gap needed to survive conservative friction assumptions

Then define a materiality ratio:  
M\_ratio \= G\_abs / max(M\_floor, epsilon)

Interpretation  
- if M\_ratio \< 1, the gap has not cleared the floor of indifference  
- if M\_ratio is around 1, the case may be watch-only or marginal  
- if M\_ratio is clearly above 1, candidate promotion becomes more defensible  
- stronger gaps support confidence only when trust is also strong

MVP1 practical rule  
If PPE cannot yet estimate these floors directly from data, it may use provisional constants, but those constants must be explicitly labeled as temporary v1 proxies rather than earned truths.

Canonical warning  
Fixed numbers are acceptable as placeholders.  
They are not the real logic.  
The real logic is: a disagreement matters only when it is large relative to the uncertainty and friction floors that surround it.

Recommended MVP1 posture  
For MVP1:  
- keep both absolute and relative gap visible  
- use trust tier as part of the implied measurement floor  
- treat low-trust states as increasing the effective floor  
- keep the floor logic explicit in provenance or verification  
- avoid pretending that a small clean gap and a large dirty gap mean the same thing

Why absolute and relative both matter  
Absolute gap matters because tiny percentage changes may be economically irrelevant even if they look large in ratio terms.  
Relative gap matters because the same absolute gap means something different in a narrow-width regime than in a wide-width regime.

Canonical short summary  
Do not ask only: how big is the gap?  
Ask: how big is the gap relative to the uncertainty and friction that surround it?

\============================================================  
7\. OUTPUT STATES  
\============================================================

PPE should not only produce candidate actions.  
It should also be able to produce a valid no-trade output.

Canonical output classes  
- candidate signal worth inspection  
- watch only  
- paper-track setup  
- acted setup  
- no-trade

No-trade as a first-class output  
No-trade is not an absence of output.  
It is a valid output class.

Canonical no-trade states should eventually include at least:  
- no candidate  
- mixed / unclear  
- insufficient trust  
- insufficient materiality  
- not executable under current conditions  
- watch only, not act

Preferred interpretation style  
When PPE returns no-trade, it should try to say why in operator-legible terms.  
For example:  
- the disagreement is too small to matter after frictions  
- the data quality is not strong enough  
- the signal is mixed across references  
- the structure is interesting but not currently executable  
- trust checks failed

Why this is load-bearing  
Without a first-class no-trade state, the system becomes subtly biased toward performative action.  
That contaminates learning and reduces trust.

\============================================================  
8\. BUILD ORDER  
\============================================================

Core principle  
Build the closed loop in dependency order.  
Do not build the most exciting thing first.  
Build the thing that makes the next thing trustworthy.

Canonical build order  
1\. represent the market  
2\. define the comparison frame  
3\. detect one narrow class of candidate opportunity  
4\. filter for trust and materiality  
5\. map to expression families and no-trade states  
6\. remember candidate outputs  
7\. review and calibrate  
8\. only then expand breadth, automation, and capital intensity

Most important rule  
Do not try to build a profitable trading engine before building a trustworthy candidate and review loop.  
If the system cannot remember what it said, what happened, and why it was wrong or right, it is not ready for broad anomaly coverage or serious trading claims.

Refined near-term build sequence for PPE  
1\. preserve and strengthen dashboard legibility  
2\. keep market and trust context visible  
3\. complete and formalize width-disagreement candidate detection  
4\. sharpen materiality, trust, and confidence semantics  
5\. make the candidate surface honest, inspectable, and witnessable  
6\. add durable candidate snapshot logging and candidate history immediately  
7\. add paper-tracking foundation and expression-family mapping  
8\. add review loop and calibration  
9\. define the go / no-go gate for a first tiny protocol-test dollar attempt  
10\. only then broaden anomaly families, automation, or stronger trade-detail logic

Why candidate memory moved earlier  
A candidate panel without durable memory risks becoming persuasive theater.  
A candidate panel plus durable memory becomes the beginning of a research machine.

What not to build yet  
- many anomaly families at once  
- exact strike optimization  
- heavy portfolio machinery  
- strong recommendation language  
- autonomous execution logic  
- broad multi-asset expansion before the first wedge is trustworthy  
- complex ML ranking before the basic loop is stable

Dependency rule  
Build the thing that makes the next thing trustworthy.  
Examples:  
- build trust filtering before broad scanning  
- build candidate history before strong profitability claims  
- build expression families before exact ticket optimization  
- build review logic before scaling automation  
- build calibration before broad capital deployment

Anti-delusion rule  
When in doubt, delay breadth and increase loop integrity.

\============================================================  
9\. ENGINEERING CLOCK VS EVIDENCE CLOCK  
\============================================================

This distinction should be treated as canon.

Engineering clock  
Tracks whether slices close cleanly, the interface improves, the system becomes more legible, and product layers get built.

Evidence clock  
Tracks whether candidates are frozen, reviewed, calibrated, compared across buckets, and shown to carry repeatable expected value after costs and uncertainty.

Canonical rule  
A clean slice can move the engineering frontier.  
It does not automatically move the evidence frontier.

Interpretation  
PPE may reach a much better product state quickly while still being far from evidence-backed edge.  
That is not failure.  
It is a different clock.

\============================================================  
10\. FIRST-DOLLAR ATTEMPTS, MEMORY, AND REVIEW  
\============================================================

First-dollar attempts are protocol tests.  
They are not victory laps.

Purpose of the first-dollar attempt  
The purpose is not to prove PPE has edge.  
The purpose is to test whether a live, bounded, attributable action can be taken under rules that were specified before the outcome.

The first-dollar attempt should answer:  
Can a real action be traced back to:  
- a frozen candidate  
- explicit trust checks  
- an expression-family rationale  
- a falsification condition  
- a review horizon  
- a bounded risk rule

If yes, the protocol is maturing.  
That still does not mean edge has been proven.

Minimum candidate snapshot schema  
The candidate layer should not mature further without durable candidate snapshots.

Each frozen candidate record should eventually contain at least:  
- candidate ID  
- timestamp  
- underlying / spot snapshot  
- expiry / horizon  
- market data source or venue  
- quote quality / stale status  
- spread or liquidity status  
- usable-strikes count or equivalent quality indicator  
- reference model or benchmark used  
- benchmark version  
- market-implied width or comparable market measure  
- reference width or comparable benchmark measure  
- disagreement magnitude  
- anomaly subtype  
- materiality score or threshold result  
- trust flags  
- confidence score  
- expression family  
- falsification condition  
- review horizon  
- candidate logic / classifier version  
- operator action state: ignored, watched, paper-tracked, or acted

Canonical rule  
If the system cannot remember what it said before the outcome, it is not yet doing real edge research.

Minimum credible learning loop  
PPE becomes a real edge-research system only when it has a minimum closed learning loop.

Minimum loop  
1\. surface a candidate under explicit rules  
2\. freeze a snapshot before outcome  
3\. assign a review horizon  
4\. record whether the operator ignored, watched, paper-tracked, or acted  
5\. review the candidate after the horizon  
6\. compare the candidate quality to the realized result  
7\. track outcomes by class, subtype, confidence bucket, and benchmark version  
8\. decide whether to continue, refine, suppress, or retire the class

Basic execution realism requirement  
Full portfolio machinery can wait.  
Basic execution realism cannot.  
Before strong claims about candidate quality, PPE should eventually adopt conservative assumptions about:  
- bid / ask reality  
- slippage  
- stale quotes  
- thin-market conditions

Canonical warning  
A disagreement that disappears inside realistic execution assumptions is not yet a useful opportunity.

\============================================================  
11\. OUTCOME DEFINITION AND REVIEW-SUCCESS CRITERIA  
\============================================================

Purpose  
This section defines what PPE means by a reviewed outcome.  
Its job is to stop review from collapsing into vague hindsight, pure vibes, or single-metric thinking.

Canonical rule  
A candidate should not be judged only by whether money was made once.  
Review should ask whether:  
- the thesis was directionally right  
- the candidate was economically meaningful  
- the proposed expression family fit the thesis  
- the setup survived realistic execution assumptions  
- the result is clean enough to teach the system something

Outcome definition must exist at three levels

Level 1: Candidate-level outcome  
Question:  
Was the flagged disagreement real, meaningful, and resolved in the expected direction over the chosen review horizon?

Candidate-level success criteria  
A candidate review should eventually ask:  
- did the disagreement actually exist under clean data?  
- was it large enough to matter after conservative frictions?  
- did the market move in the direction implied by the candidate thesis?  
- did the disagreement compress, persist, or worsen over the review horizon?  
- was the candidate mixed, noisy, or not judgeable in hindsight because the inputs were weak?

Interpretation  
This level is about thesis quality, not trade construction quality.  
A candidate can be good even if no trade was placed.  
A candidate can also fail even if a lucky trade would have made money.

Level 2: Paper-tracked setup outcome  
Question:  
If the candidate had been expressed using the chosen expression family under conservative assumptions, would the setup have behaved as expected?

Paper-tracked success criteria  
A paper-tracked review should eventually ask:  
- did the chosen expression family fit the thesis?  
- would conservative fills still leave the setup economically meaningful?  
- was the payoff shape aligned with the actual path of market movement?  
- did the setup hit falsification before the expected thesis resolution?  
- did the setup produce a positive, neutral, or negative result under the stated review horizon?

Interpretation  
This level is about expression quality and protocol realism.  
It sits between pure candidate logic and real-money execution.

Level 3: Acted-setup outcome  
Question:  
Did a real bounded action behave in a way that validates both the protocol and the economic idea?

Acted-setup success criteria  
An acted review should eventually ask:  
- was the action taken under the stated rules?  
- was the setup attributable to a frozen candidate?  
- did execution stay within expected friction bounds?  
- did the setup produce the intended kind of payoff behavior?  
- did the outcome support, weaken, or invalidate the candidate class?

Interpretation  
This level is not just about P&L.  
It is also about whether the live protocol is clean enough to trust future evidence.

Canonical review buckets  
Every reviewed case should eventually land in one of a small number of buckets.  
Suggested review buckets:  
- thesis right, expression right  
- thesis right, expression weak  
- thesis mixed, expression irrelevant  
- thesis wrong, expression irrelevant  
- not judgeable due to bad inputs or poor witnessability  
- execution-contaminated result

Why this matters  
Without buckets, the system tends to overlearn from lucky wins and underlearn from structurally useful failures.

Minimum review fields  
Each reviewed candidate should eventually record at least:  
- review date  
- realized outcome status  
- thesis outcome bucket  
- expression outcome bucket  
- execution realism verdict

\============================================================  
13\. CLOSED-LOOP MVP1 AND PHASE ARCHITECTURE  
\============================================================

MVP name  
PPE Closed-Loop MVP 1: Auditable BTC ATM-Width Disagreement Research Loop

Why this is the correct first MVP  
This MVP is the first full honest research chain.  
Its purpose is not to prove edge.  
Its purpose is to prove that PPE can complete one narrow end-to-end loop cleanly enough to learn from it.

Fixed product scope for MVP1  
- BTC only  
- exactly one anomaly family only  
- exactly one subtype first: ATM width disagreement  
- one explicit benchmark for candidate generation  
- candidate generation uses the current system reference distribution, not arbitrary operator belief  
- belief overlay may remain visible, but it does not drive candidate generation in MVP1  
- market-implied distribution must be trustworthy enough for candidate generation  
- if the market-implied path is unavailable or too degraded, no candidate may be produced  
- output state must resolve to exactly one of: candidate / watch only / no-trade  
- no-trade is first-class  
- expression mapping is family-level only  
- no exact strikes  
- no executable ticket generation  
- no autonomous execution  
- the existing implied-lab / dashboard remains the anchor

The first full chain  
1\. show BTC market and trust context  
2\. define one explicit benchmark  
3\. detect one anomaly type only: ATM width disagreement  
4\. apply trust and materiality gates  
5\. output exactly one of: candidate / watch only / no-trade  
6\. map candidate to an expression family  
7\. freeze the evaluation before outcome  
8\. assign a review horizon  
9\. review later under explicit criteria  
10\. aggregate reviewed cases at class level

What this MVP must not do  
- no multiple anomaly families  
- no exact strike optimization  
- no autonomous execution  
- no portfolio machinery  
- no broad scanner  
- no multi-asset expansion  
- no ML ranking  
- no edge-proven language

Phase architecture

Phase 1 — Market + benchmark substrate  
Purpose:  
Create the minimum reliable substrate for ATM width-disagreement evaluation.

Must include:  
- clear BTC market context  
- explicit benchmark identity  
- market width and benchmark width on the same horizon  
- visible trust state  
- honest degraded-state handling

Done when:  
- market width is visible  
- benchmark width is visible  
- benchmark identity is explicit  
- trust state is explicit  
- the system can honestly say it cannot evaluate a candidate yet

Must exclude:  
- candidate promotion logic  
- confidence tiers  
- output decision logic  
- snapshot persistence  
- review engine  
- class summaries

Phase 2 — ATM width-disagreement engine v1  
Purpose:  
Turn the substrate into one narrow classification engine.

Must include:  
- ATM width gap calculation  
- absolute and relative gap calculation  
- materiality logic  
- trust gating  
- classification labels:  
  - market too wide  
  - market too narrow  
  - mixed / unclear  
  - insufficient trust  
  - insufficient materiality

Done when:  
- the system can classify a valid run deterministically  
- the logic is explicit enough to explain  
- low-trust states do not promote candidates

Must exclude:  
- rich candidate UX  
- snapshot persistence  
- review logic  
- class aggregation  
- additional anomaly families

Phase 3 — Candidate / watch / no-trade decision surface  
Purpose:  
Make the classifier operationally legible to the human operator.

Must include:  
- single primary output state  
- explanation  
- confidence tier  
- expression-family mapping  
- falsification condition  
- review horizon  
- first-class no-trade reasoning

Done when:  
- the operator can understand the current evaluation in plain language  
- candidate / watch / no-trade is explicit  
- the dashboard remains the anchor

Must exclude:  
- snapshot persistence  
- review screens  
- class learning summaries  
- exact strategy selection

Phase 4 — Snapshot + memory layer  
Purpose:  
Freeze outputs before outcome.

Must include:  
- explicit freeze action  
- durable snapshot persistence  
- retrieval of frozen cases  
- benchmark version capture  
- classifier version capture

Done when:  
- the operator can freeze candidate / watch / no-trade evaluations  
- frozen records persist and can be reopened  
- later review is possible because witnessability exists

Must exclude:  
- full review engine  
- class-level analytics  
- auto-logging every UI change

Phase 5 — Review engine  
Purpose:  
Review frozen cases later under explicit outcome criteria.

Must include:  
- review-horizon handling  
- candidate-level review  
- realized outcome status  
- supportive / contradictory / contaminated logic  
- review notes  
- lightweight family-level paper-tracking support if feasible

Done when:  
- a frozen case can be reopened and reviewed  
- review statuses are finite and explicit  
- contaminated / not judgeable is supported

Must exclude:  
- real-money execution logic  
- full ticket-level paper-trade engine  
- class-level decision automation beyond basic summaries

Phase 6 — Class-level learning summaries  
Purpose:  
Aggregate reviewed cases into usable research feedback.

Must include:  
- counts by direction  
- counts by confidence  
- counts by trust  
- counts by benchmark version  
- counts by classifier version  
- simple continue / refine / suppress / retire summary

Done when:  
- the system can summarize reviewed ATM-width cases at class level  
- the operator can see whether the class is getting stronger or weaker as evidence accumulates

Must exclude:  
- automated live capital deployment  
- broad anomaly scanning  
- strategy optimization  
- portfolio / risk engine

Delegation rule for later planning  
At the product level, PPE defines:  
- the MVP chain  
- the phase boundaries  
- the phase done conditions  
- the anti-scope-creep rules

At the implementation level, the coding agent may define:  
- slices inside phases  
- technical implementation order  
- validation design  
- repo-specific architecture choices

\============================================================  
14\. PRODUCT GOVERNANCE CONTRACT  
\============================================================

Output-state precedence  
MVP1 must resolve the primary output state in this order:  
1\. invalid market-implied path or invalid benchmark path -> no-trade  
2\. low-trust state -> no-trade  
3\. mixed / unclear disagreement -> watch only or no-trade  
4\. insufficient materiality -> no-trade  
5\. marginal but valid disagreement -> watch only  
6\. clear, material, high-trust disagreement -> candidate

Data-quality taxonomy  
Use three canonical data-quality states:  
- usable  
- degraded  
- invalid

Allowed behavior by quality state:  
- usable -> candidate / watch only / no-trade  
- degraded -> watch only / no-trade  
- invalid -> no-trade only

Benchmark and versioning contract  
Every frozen evaluation should be attributable to explicit product logic versions.  
Minimum required versioning fields are:  
- benchmark ID  
- benchmark version  
- candidate logic / classifier version  
- materiality-rule version  
- review-rule version  
- expression-mapping version

Review-horizon defaults  
MVP1 review-horizon defaults are:  
- the default review horizon is the selected expiry / horizon active when the evaluation was frozen  
- frozen cases keep the horizon they were born with  
- later benchmark or UI changes must not retroactively rewrite old frozen cases  
- custom multi-horizon review logic is later scope, not MVP1 scope

Authority rule  
This master document is authoritative for:  
- product logic  
- MVP scope  
- phase boundaries  
- done conditions  
- anti-scope-creep rules

The coding agent may decide:  
- slice decomposition  
- technical architecture  
- file/module boundaries  
- validation implementation

The coding agent may not decide without explicit approval:  
- to broaden anomaly scope  
- to promote exact-ticket logic into MVP1  
- to weaken no-trade as a first-class output  
- to move autonomous execution forward  
- to reinterpret the benchmark contract or review contract materially

\============================================================  
15\. MVP1 PRODUCT BEHAVIOR CONTRACT  
\============================================================

Purpose  
This section defines MVP1 at the product-behavior level so the coding agent does not need to infer operator flow, state behavior, or field-level expectations.
