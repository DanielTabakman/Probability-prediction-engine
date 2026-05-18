---
title: "PPE Master (MVP1 controlling canon)"
source: "d:/Users/User/Downloads/PPE Master — Vision, Canon, Build Order, and Current Audit (2).md"
imported_utc: "2026-05-18"
control_rule: "For MVP1 implementation, MVP1-specific sections override broad canon if they appear to conflict."
addendum:
  - "2026-05-04: Conversation-mode + roadmap vocabulary (from Audit (1).md)"
  - "2026-05-18: Full re-import; §1A order, §12 audit, §1A deployment surfaces, §15A repo-truth (from MVP1_FRONTIER + src/)"
live_steering: "docs/SOP/MVP1_FRONTIER.md overrides stale phase-order language in §12 when they differ."
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
9\. Section 15A — MVP1 implementation status (repo-truth)

Why this reading order  
It gives the agent:  
\- the project’s purpose first  
\- the reusable system logic second  
\- the active wedge third  
\- the current-state placement fourth  
\- the fixed MVP contract fifth  
\- the exact behavior contract sixth  
\- what is already shipped vs still aspirational seventh

Canonical summary  
The code should flow downward from the controlling contract.  
Corrections should flow upward from evidence.  
Neither direction should bypass the document.

Conversation-mode rule  
This document is used for both vision steering and implementation steering.  
When the user asks to discuss vision, naming, strategy, product architecture, conceptual direction, or the relationship between the North Star and MVP, respond conversationally and strategically.  
Do not provide Cursor prompts, agent prompts, repo implementation instructions, or copy-paste execution blocks unless the user explicitly asks for one using phrases such as: for Cursor, agent prompt, implementation prompt, turn this into a slice, or make this actionable for the repo.  
If an implementation step seems relevant during a strategy conversation, mention it briefly as an option, but do not generate a copy-paste block by default.

Discussion-mode default  
For vision conversations, treat the goal as conceptual clarity, altitude separation, decision quality, and roadmap coherence.  
For implementation conversations, treat the goal as bounded execution, repo truth, validation, and closeout evidence.  
Do not silently switch from discussion mode to implementation mode.

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
1A. VALIDATION PHASE, PRODUCT SURFACES, AND PRODUCTION SPINE  
\============================================================

Purpose of this section  
This section exists because PPE needs near-term validation without collapsing the long-term vision into premature claims.  
The operator needs real contact with reality soon: people who understand and might pay, a narrow strategy protocol that can be tracked, and a coherent production chain that explains why each next addition belongs.

Accepted roadmap vocabulary  
This section defines the current working vocabulary for vision-aware roadmap planning.  
These terms are intended to reduce altitude collapse and help translate between strategy, validation, and build execution.

Strategic layer  
End-State Vision: the long-term commercial destination of PPE.  
Product Surface: a sellable or user-facing manifestation of PPE.  
Core Engine: the shared underlying machinery that supports product surfaces and future capabilities.  
Wedge: a narrow proof-of-system domain used to make progress without broadening too quickly.  
Protocol: a repeatable research or strategy rule, usually of the form when X is observed, do Y, then review Z.

Roadmap layer  
Roadmap Chapter: a major product maturity movement or development chapter.  
Reality Check: a real-world validation test showing whether PPE matters in contact with customers, markets, operators, or strategy evidence.  
Strategic Lever: a high-leverage product or system addition chosen because it advances the vision and improves one or more validation lanes.

Build layer  
Epic: a large coherent build package that can be decomposed by Cursor or an implementation agent.  
Slice: the smallest meaningful product change that can be validated and closed.  
Task: a concrete implementation step inside a slice.

Sync layer  
Frontier Sync: the ritual for keeping the vision frontier and build frontier aligned.  
Steering Delta: the vision-to-build update.  
Build Delta: the build-to-vision update.

Canonical hierarchy interpretation  
The normal top-down flow is:  
End-State Vision \-\> Product Surface / Core Engine \-\> Roadmap Chapter \-\> Reality Check / Strategic Lever \-\> Epic \-\> Slice \-\> Task

The normal bottom-up flow is:  
Task \-\> Slice \-\> Epic \-\> Build Delta \-\> Frontier Sync \-\> roadmap adjustment \-\> master-doc update if needed

Translation-layer rule  
The roadmap layer translates top-down vision into bottom-up build reality.  
It should decide which Reality Checks and Strategic Levers matter next before Cursor decomposes work into epics, slices, and tasks.

Two-pull roadmap rule  
PPE should be roadmaped through two intentional pulls:  
1\. Vision pull: the North Star, Anomaly Desk, Belief-to-Trade Engine, and PPE Core should keep pulling the project upward toward the larger commercial and strategic possibility.  
2\. Validation pull: near-term milestones should deliberately create reality contact through demos, users, payment, paper-tracked protocols, reviewed cases, and clearer operator confidence.

Canonical interpretation  
The larger vision should pull the roadmap upward.  
The current validation need should pull the roadmap toward useful near-term proof.  
Neither pull should erase the other.  
A good roadmap item advances the vision while creating validation, as long as it does not create major detour cost or weaken the core loop.

Vision-effective efficiency rule  
Useful validation milestones are preferred when they also strengthen the general path.  
Do not reject a milestone merely because it is commercially useful or emotionally validating.  
Reject it only if it creates major complexity, undermines loop integrity, or distracts from the core engine without enough learning value.

Canonical validation rule  
Do not force one milestone to satisfy all validation needs.  
PPE should track three related but different validation clocks:  
1\. commercial validation  
2\. market / edge validation  
3\. system / engine validation

Reality Check concept  
A Reality Check is a real-world validation test, analogous to a software test but aimed at the market, customer, operator, or strategy environment rather than the codebase.  
Reality Checks are used to test whether PPE is becoming useful, sellable, understandable, reviewable, or economically meaningful outside the internal build process.

Reality Checks are not vibes.  
They should be observable enough that the operator can say whether reality responded.

Examples:  
\- a potential customer understands the demo in under five minutes  
\- a potential customer asks to use the product again  
\- a person agrees to pay for a beta, research brief, or call  
\- a user says the anomaly brief would save them real effort  
\- ten candidate cases are frozen and later reviewable  
\- a paper-tracked protocol produces clean reviewed cases  
\- a micro-sized real action can be traced back to a frozen candidate and reviewed without hindsight rewriting

Canonical rule  
Reality Checks are the external complement to software validation.  
Tests ask whether the program works as intended.  
Reality Checks ask whether the program matters in contact with the world.

Three validation clocks

Commercial validation  
Question: Can a real person understand the product, want it, and pay for it?  
This clock is advanced by demos, user reactions, pricing tests, paid beta signups, research briefs, client calls, and willingness to pay.  
Commercial validation does not require proven edge.  
It requires clear, useful, honest market insight that someone values.

Market / edge validation  
Question: Are any repeated candidate protocols becoming economically meaningful over time?  
This clock is advanced by frozen candidates, paper-tracked setups, reviewed outcomes, friction-aware protocol tests, and eventually small bounded acted setups.  
This clock moves more slowly than the commercial clock.  
Do not call a strategy positive-EV until repeated reviewed evidence survives costs, slippage, uncertainty, bad cases, and regime changes.

System / engine validation  
Question: Is the underlying PPE engine becoming coherent enough to guide future work?  
This clock is advanced when the project can explain its own production chain, identify the weakest current layer, and choose the next addition because it improves trustworthiness, usability, sellability, or learning.

Nervous-system validation note  
Near-term validation is not only a business need.  
It is also a stabilizing operator need.  
Paid interest, reviewable strategy protocols, and a clear production spine reduce ambiguity load and help the operator keep building without relying only on abstract belief in the vision.  
This is legitimate.  
The project should support healthy validation without responding to validation hunger by overclaiming edge or rushing automation.

Accepted current roadmap chapter and order  
Current Roadmap Chapter: Validation Chapter — Demoable Research Cockpit \+ Evidence-Generating Loop.

Purpose:  
Make PPE understandable, showable, sellable, and evidence-generating without claiming proven edge.

Accepted near-term Reality Checks:  
1\. Demo clarity: a potential user understands what PPE is showing quickly.  
2\. Paid interest: a real person expresses willingness to pay, join a paid beta, buy a research brief, or book a paid call.  
3\. First reviewable protocol cases: PPE produces frozen cases that can be reviewed later.  
4\. Manual NVIDIA / LEAPS brief: test whether a customer values thesis-to-options translation before building broad multi-asset automation.

Accepted near-term Strategic Levers:  
1\. Validate the MVP1 closed loop (freeze → review → class summary) with real operator cases.  
2\. Demo UX and deployment surfaces (public demo vs full app; see **Deployment surfaces** below).  
3\. Contract gaps vs §15: `primary_output_state`, explicit materiality floors, fuller frozen-field witness.  
4\. Phase 2 desirability / playability (parallel track; `docs/SOP/PHASE_2_CHARTER.md`) without widening MVP1 scope.  
5\. Demo script and anomaly / research brief format.  
6\. Manual NVIDIA / LEAPS Reality Check (low-drag, separate from BTC MVP1 build).

Accepted order (repo-truth, 2026-05):  
1\. **Validate** Phases 1–6 v0 in `src/` (substrate through class summary per `docs/SOP/MVP1_FRONTIER.md`) — regression smoke, manual freeze/review path, evidence-clock discipline.  
2\. **Sharpen** decision-surface and witnessability gaps (§15A) — do not treat “memory missing” as the next greenfield build.  
3\. **Ship** demo-ready UX on `marketstructureos.com` (tutorial, theme, compact MVP1 lab default, optional **Get full access** CTA to full app).  
4\. **Run** customer Reality Checks (demo clarity, paid interest, reviewable frozen cases).  
5\. **Run** manual or semi-manual NVIDIA / LEAPS customer-discovery brief as a separate low-drag experiment.

Rationale:  
Freeze/history and review v0 already exist; the credibility lever for demos is **using** that loop in front of users, plus honest copy that does not overclaim edge. Public demo should show legibility and discipline; the full app hostname carries snapshots and reviews when enabled.

Deployment surfaces (operator env; see `README.md`, `.env.example`, `docs/SOP/DEMO_UI_RELEASE_CHECKLIST.md`):  
\- **Public demo** (`PPE_ENABLE_SNAPSHOTS=0`): no server-side snapshot history; optional `PPE_PRIVATE_APP_URL` (HTTPS) shows **Get full access** → full app.  
\- **Full app** (`PPE_ENABLE_SNAPSHOTS=1`, optional `PPE_SNAPSHOT_DB_PATH`): freeze, reopen, reviews, class summary.  
\- **MVP1 compact lab** (default): strike/payoff/ticket chrome hidden unless `PPE_POST_MVP1_LAB_UI=1`.  
\- **Debug UI**: `PPE_SHOW_DEBUG_UI=1` exposes performance/debug expanders (default off).  
\- In-app / tab title: **Probability Engine** (`src/viz/app.py`).

Current validation-phase goal  
The next chapter should be understood as a validation phase:  
make PPE demoable, sellable, and evidence-generating without pretending it has proven edge yet.

Validation-phase targets  
1\. A demo people can understand quickly.  
2\. A small paid-beta or research-offer surface.  
3\. One narrow paper-tracked strategy protocol.  
4\. A clear production-chain map for deciding what to add next.

Product / platform architecture hypothesis  
The emerging external product architecture is:  
\- PPE Labs as the umbrella company / lab identity  
\- Market Structure OS as the main website and software platform  
\- PPE Lab as each user’s personal workspace for belief-to-strategy construction  
\- named modules underneath the platform for specific jobs such as market map, belief builder, anomaly desk, expression engine, freeze ledger, review board, and protocol tracker

Market Structure OS purpose  
Market Structure OS is the base environment.  
It shows the market as the default: what current prices, volatility, distribution, width, skew, term structure, and trust signals imply.  
Its job is to make market structure legible before the user changes anything.

PPE Lab purpose  
PPE Lab is the user’s personal strategy-construction layer.  
It allows a user to start from the market default, change the variables or assumptions they disagree with, and ask PPE to translate the resulting disagreement into a candidate view, expression family, paper-trackable setup, and eventually a more complete strategy plan.

Current-stage boundary  
For the validation chapter, this architecture is a naming and product-vision container, not an implementation expansion.  
The current build remains narrow: BTC-first, one wedge first, candidate / watch / no-trade, freeze/history, review, and evidence discipline.  
Market Structure OS and PPE Lab should help explain the future product shape without broadening MVP1 scope prematurely.

Aspirational execution note  
Long term, the belief-to-execution chain may become: market default \-\> user belief change \-\> explicit disagreement \-\> candidate expression \-\> strategy construction \-\> execution plan \-\> monitoring \-\> review \-\> learning.  
Eventually, PPE may aspire to produce or execute an optimal strategy relative to the user’s belief, constraints, risk limits, and market conditions.  
This remains aspirational until review density, execution realism, risk control, and evidence-backed class learning justify it.

Near-term sellable product surface  
The first sellable surface is the PPE Research Cockpit or Anomaly Brief.  
The honest product promise is:  
PPE makes BTC options market structure legible, identifies candidate disagreements worth inspecting, explains trust and materiality, and preserves what was seen for later review.

Allowed near-term commercial forms  
\- private demo plus paid beta  
\- weekly BTC volatility / anomaly brief  
\- bespoke anomaly research call  
\- small-client research cockpit pilot  
\- operator-assisted market-structure readout

Commercial boundary  
Do not sell guaranteed profit.  
Do not sell proven alpha before the evidence clock earns it.  
Sell legibility, research discipline, anomaly inspection, and decision-support clarity.

Customer asset-expansion signal  
A potential customer specifically described wanting NVIDIA exposure through LEAPS and having to manually sift through many options to find the best expression.  
This is an important commercial signal because it points toward a customer-facing desire for cross-asset options search, expression comparison, and answer-generation.

Interpretation  
The customer does not merely want BTC market legibility.  
They want help translating a thesis about a major tradable asset into a specific options exposure.  
This is closely aligned with the long-term Belief-to-Trade Engine.

Major-asset ambition  
The commercial product should eventually support major tradable assets beyond BTC, including large liquid equities, indices, ETFs, and other major optionable instruments where data quality and liquidity are sufficient.  
Examples include names like NVIDIA, but the principle is broader: major tradable assets with enough options liquidity to support useful comparison.

Expansion caution  
Multi-asset support may be commercially important, but it can increase data complexity, testing cost, quote-quality burden, UI complexity, and iteration drag.  
Do not let broad asset coverage weaken the first closed loop.

Roadmap implication  
Treat multi-asset / NVIDIA-style thesis-to-options support as a commercial pull and later product surface, not as an immediate reason to abandon the BTC-first MVP loop.  
The near-term roadmap should look for low-drag ways to learn from this demand, such as:  
\- demoing the BTC cockpit as a proof of concept  
\- designing the eventual cross-asset workflow conceptually  
\- testing a manual or semi-manual NVIDIA LEAPS research brief before automating full multi-asset support  
\- identifying what shared core infrastructure would transfer from BTC to other optionable assets

Near-term strategy-validation surface  
The first strategy-validation object should be a protocol, not a claim of proven edge.  
Example protocol form:  
When market ATM width is materially wider than the benchmark, data quality is usable, and the gap clears the current materiality floor, classify as a short-vol-family candidate, freeze the case, paper-track it, and later review whether width compressed or the expression family would have behaved as expected.

Inverse protocol form:  
When market ATM width is materially narrower than the benchmark, data quality is usable, and the gap clears the current materiality floor, classify as a long-vol-family candidate, freeze the case, paper-track it, and later review whether width expanded, repriced, or produced the expected expression-family behavior.

Strategy maturity ladder  
thesis \-\> candidate rule \-\> paper-tracked rule \-\> micro-size protocol \-\> acted strategy \-\> evidence-backed edge

Canonical warning  
A protocol can be useful before it is proven.  
A useful protocol is not yet positive-EV.  
The goal of the first protocol is to create clean, reviewable cases and begin separating signal from persuasive noise.

Underlying production spine  
PPE Core should be understood as this production chain:  
Sense \-\> Represent \-\> Benchmark \-\> Detect \-\> Gate \-\> Express \-\> Control \-\> Remember \-\> Review \-\> Learn \-\> Package

Layer questions  
Sense: What is the market saying?  
Represent: Can the system show it clearly?  
Benchmark: Relative to what is the market being judged?  
Detect: What looks meaningfully different?  
Gate: Is the data trustworthy and the gap material?  
Express: What kind of expression family would fit the view?  
Control: Should the operator ignore, watch, paper-track, act, or output no-trade?  
Remember: What did PPE say before the outcome?  
Review: What happened later?  
Learn: Which setup classes should be promoted, refined, suppressed, or retired?  
Package: How does this become something people understand, use, and pay for?

Three roadmap lanes  
The roadmap should be understood as three lanes that move together but do not mature at the same speed.

Lane 1: Product / customer  
Goal: make something people understand, want, and pay for.  
This lane includes demo clarity, paid beta offers, anomaly briefs, client conversations, onboarding, pricing, and customer feedback.

Lane 2: Research / edge  
Goal: create tracked protocols that may become evidence-backed edge over time.  
This lane includes candidate rules, freeze, paper-tracking, review, class summaries, micro-size protocol tests, and eventually acted setups.

Lane 3: Core engine  
Goal: build the underlying machinery that supports both product surfaces and the long-term North Star.  
This lane includes sensing, representation, benchmark, detection, gating, expression, control, memory, review, learning, and packaging.

Lane interaction rule  
A strong roadmap item should state which lane it primarily advances and which secondary lanes it supports.  
The best near-term items usually advance at least two lanes, and the best milestones often advance all three.

Production-loop architecture  
PPE should make decisions through three production loops.

Customer / product loop  
Question: Can a person understand it, want it, and pay for it?  
Flow: demo \-\> user reaction \-\> objection \-\> pricing test \-\> paid beta \-\> feature priority.  
This loop decides what to package.

Research / edge loop  
Question: Are the signals becoming more real?  
Flow: candidate \-\> freeze \-\> paper-track \-\> review \-\> class summary \-\> promote / refine / suppress / retire.  
This loop decides what to trust.

Engine / build loop  
Question: What layer of the engine is weakest right now?  
Flow: identify bottleneck \-\> add smallest missing capability \-\> validate \-\> update roadmap.  
This loop decides what to build next.

Triple-use milestone rule  
Prefer roadmap items that serve all three validation needs at once:  
1\. they make the product easier to demo, understand, or sell  
2\. they make the strategy protocol more trackable, reviewable, or evidence-generating  
3\. they strengthen PPE Core

Triple-use examples  
\- benchmark clarity  
\- candidate / watch / no-trade explanation  
\- freeze and history  
\- anomaly brief format  
\- review loop  
\- class-level summary

Selection preference  
A milestone that improves commercial validation, research / edge validation, and engine validation should usually outrank a milestone that serves only one lane, unless the single-lane item removes a major blocker.

Production selection rule  
Every proposed addition should answer at least one of these questions:  
1\. Does it improve commercial validation?  
2\. Does it improve research / edge validation?  
3\. Does it improve system / engine validation?  
4\. Does it make the next layer more trustworthy, usable, sellable, or reviewable?

If a proposed addition improves none of these, it waits.

Priority interpretation  
The fastest near-term validation is likely commercial validation through a clear demo, paid beta, or anomaly brief.  
The deepest long-term validation is likely the research / edge loop through repeated reviewed cases.  
The operator-stabilizing validation is likely the system / engine loop through a visible production spine.

Frontier Sync protocol  
PPE may have two active frontier workstreams at once:  
1\. a vision / strategy frontier that updates product direction, roadmap logic, customer signals, terminology, validation priorities, and master canon  
2\. a build / Cursor frontier that changes the software, discovers constraints, and returns evidence from implementation reality

This is efficient, but it creates synchronization risk.  
The risk is that either side continues from stale assumptions while the other side has moved forward.

Canonical sync rule  
After any major Cursor return, major vision update, roadmap change, customer signal, or master-doc update, the two frontiers should exchange concise deltas before the next meaningful work unit is selected.

Frontier Sync  
A Frontier Sync is the brief ritual that keeps the vision frontier and build frontier aligned.  
It does not need to happen after every small message.  
It should happen at selection boundaries, after material discoveries, after major closeouts, or when either side may be operating from stale context.

Steering Delta  
A Steering Delta is the update from the vision / strategy side to the build side.  
It should include:  
\- what changed in vision, roadmap, terminology, customer signal, or priority  
\- why it matters  
\- whether it applies now or later  
\- what should continue unchanged  
\- what should not be built yet

Build Delta  
A Build Delta is the update from Cursor / implementation reality to the vision side.  
It should include:  
\- what changed in the product or codebase  
\- what new capability now exists  
\- what constraints, costs, bugs, or technical realities were discovered  
\- whether the current roadmap still looks feasible  
\- what product assumptions may need to be reconsidered

Parallel-work rule  
Vision work may continue while Cursor or an implementation agent is building, but no new implementation unit should be selected from stale roadmap assumptions after a material master-doc update or major Build Delta.

Active-build protection rule  
Do not interrupt an active build merely because a vision clarification occurred unless the change reveals a direct contradiction, safety issue, scope violation, or likely waste of effort.  
Most vision updates should be applied at the next selection boundary.

Bidirectional correction rule  
The master doc controls high-level product direction.  
Cursor output provides evidence from implementation reality.  
Neither side should silently overwrite the other.  
When they differ, the mismatch should be surfaced explicitly and resolved through a Frontier Sync before the next major selection.

Canonical summary  
Frontier Sync prevents drift between the product vision and the actively built software.  
Steering Delta tells the build frontier what changed in strategy.  
Build Delta tells the vision frontier what changed in reality.

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

Naming and altitude-separation rule  
Probability Prediction Engine is the umbrella and North Star project name.  
The name is aspirational, not a current-stage performance claim.  
The gap between the North Star and the current MVP is the roadmap, not a contradiction and not a naming failure.

Do not relitigate the PPE name unless the project is being packaged for external marketing, legal/compliance review, customer-facing sales, or the product output itself starts making claims beyond its evidence level.

Canonical altitude map  
\- PPE \= North Star umbrella and project identity  
\- PPE Core \= shared infrastructure: market sensing, representation, benchmark, detection, trust gating, expression, memory, review, and learning  
\- PPE Research Cockpit \= current operator-facing product wedge  
\- BTC ATM Width Research Loop \= current MVP1 proof-of-system loop  
\- PPE Anomaly Desk \= anomaly / client opportunity product surface built on the same core infrastructure  
\- PPE Belief-to-Trade Engine \= long-term commercial application where a user can input beliefs about the world and the system translates them into market views, trading strategies, execution plans, monitoring, alerts, and eventually bounded automation

Canonical platform architecture and naming stack  
The current naming architecture is:  
\- PPE Labs \= company / creator / umbrella entity  
\- Market Structure OS \= base platform and operating layer for seeing market structure  
\- PPE Lab \= the user’s personal belief-to-strategy workspace inside Market Structure OS  
\- PPE Core \= underlying engine infrastructure that powers both Market Structure OS and PPE Lab  
\- PPE Research Cockpit \= current BTC-first cockpit / MVP-facing surface  
\- PPE Anomaly Desk \= research / anomaly-inspection surface that may become a sellable brief or client workflow  
\- Expression Engine \= future translator from belief/disagreement into candidate payoff and strategy families  
\- Freeze Ledger \= memory layer for preserving what was seen before outcome  
\- Review Board \= review and learning layer for determining what held up later

Market Structure OS interpretation  
Market Structure OS is the base layer that shows what the market currently implies.  
It should make price, volatility, distribution, width, skew, term structure, trust, and benchmark context legible enough that a user can understand why the price is the way it is and how different parts of the market relate to each other.

PPE Lab interpretation  
PPE Lab is the personal construction workspace on top of Market Structure OS.  
The user can keep most market assumptions at their default state, change the variables they disagree with, and ask the system to translate that disagreement into candidate views, expression families, paper-trackable setups, and eventually strategy plans.

Complexity-ramp rule  
New users should be able to stay at the Market Structure OS level and simply understand the market.  
Advanced users should be able to move into PPE Lab and manipulate beliefs, assumptions, candidate expressions, and reviewable protocols.  
The naming system should support this ramp instead of forcing every user into full complexity immediately.

Altitude-collapse warning  
Do not collapse the North Star, current MVP, anomaly product, infrastructure layer, and next implementation slice into one object.  
When evaluating a proposal, first identify which altitude it belongs to: North Star, Core, Research Cockpit, Anomaly Desk, MVP1 loop, or implementation slice.

Commercial North Star  
The long-term commercial product is a belief-to-trade engine.  
The desired end state is that a user can express beliefs about the world, and PPE can translate those beliefs into market views, candidate strategies, execution plans, monitoring, and alerts at key decision times.  
Automation may become part of the long-term system only after the relevant research, control, risk, and review layers are mature enough.

Long-term optimal-strategy aspiration  
The aspirational end state is that a user can begin with the market default, change only the variables they disagree with, and have PPE translate that difference through the full chain from belief \-\> market disagreement \-\> candidate expression \-\> strategy construction \-\> execution plan \-\> monitoring \-\> review.

At the highest maturity level, PPE may eventually recommend or execute an optimal strategy relative to the user’s stated belief, constraints, risk limits, account context, and market conditions.

Canonical constraint  
This is a North Star capability, not a current-stage claim.  
PPE may describe this as the direction of travel, but current MVP1 must not imply optimal strategy selection, exact-ticket authority, autonomous execution, guaranteed profit, or proven edge.

Maturity ladder for this aspiration  
1\. market default is visible  
2\. user belief differs from market default  
3\. disagreement is made explicit  
4\. candidate expression families are suggested  
5\. paper-trackable setups are constructed  
6\. reviewable execution plans are produced  
7\. bounded acted protocols are tested  
8\. evidence-backed strategy classes emerge  
9\. only later, constrained optimization and automation become legitimate

Interpretation  
The phrase optimal strategy is allowed as aspirational internal language only when it means optimal relative to explicit assumptions, constraints, evidence, and risk rules.  
It must not be used as a current product promise until the research, review, calibration, execution-realism, and risk-control layers have earned it.

Parallel anomaly product  
A second product surface is the anomaly desk: using the same market-sensing and benchmark infrastructure to find inconsistencies, anomalies, and candidate mispricings that can be shared with clients or reserved for the operator’s own opportunity pipeline.  
This is related to the belief-to-trade engine but is not identical to it.

Current MVP relationship to the North Star  
MVP1 is not the commercial end state.  
MVP1 is the first narrow proof that PPE can evaluate one BTC market-structure disagreement honestly, explain it, freeze it, and review it later.  
Its job is to earn the infrastructure and evidence habits that the larger vision will eventually require.

Current-stage naming rule  
Use current-stage language for current-stage outputs.  
Allowed current-stage terms include: research cockpit, candidate disagreement, candidate anomaly, watch only, no-trade, frozen case, reviewed case, paper-tracked setup, and evidence-backed edge only when earned.  
Do not use current-stage outputs to imply guaranteed prediction, guaranteed mispricing, autonomous trading authority, or proven profitability.

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
\- not a guarantee of mispricing  
\- not a promise of profit  
\- not a substitute for risk management  
\- not yet an autonomous trading engine  
\- not yet a full probability engine in the strong evidence-backed sense

The most important ladder  
Pattern \-\> Disagreement \-\> Candidate Anomaly \-\> Candidate Signal \-\> Paper-Tracked Setup \-\> Acted Setup \-\> Evidence-Backed Edge

Definitions  
\- Pattern: something visible in the market representation.  
\- Disagreement: a meaningful difference between market structure and a chosen reference.  
\- Candidate anomaly: a disagreement that looks unusual enough to inspect.  
\- Candidate signal: a candidate anomaly that survives initial filtering and seems worth attention.  
\- Paper-tracked setup: a candidate that has been frozen before outcome under explicit review rules.  
\- Acted setup: a setup that is actually implemented under bounded rules.  
\- Evidence-backed edge: a class of setups that shows repeatable positive expected value after costs, uncertainty, and review.

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

PPE's native stack  
If PPE is understood on its own terms, rather than only as a business wrapper, prediction engine, or arbitrage searcher, its native stack is:

1\. Market sensing  
What is the market actually saying right now?  
This layer gathers and stabilizes the raw market and trust inputs.  
Its job is to see clearly, not to judge.

2\. Representation  
Turn raw market data into a legible world-model.  
This is where surface, distribution, width, skew, peak, and structure become operator-visible.  
Its job is to make the invisible visible.

3\. Reference / benchmarking  
Relative to what should the market be judged?  
Without this layer, the system has pictures but not anomalies.  
For MVP1, the operative benchmark is the system reference distribution.

4\. Disagreement detection  
Where does market structure differ from benchmark structure?  
This is where the system produces candidate mismatches such as width disagreement.  
This is not yet trade logic.  
It is structured detection.

5\. Truth gating  
Does the disagreement survive contact with reality?  
This layer filters by trust, materiality, degradation, mixedness, and execution realism.  
Its job is to prevent PPE from becoming an impressive-looking noise machine.

6\. Judgment  
What is the system's actual conclusion?  
At minimum for MVP1, this resolves toward candidate, watch only, or no-trade.  
This is the first true decisional layer.

7\. Expression  
If the judgment mattered economically, what family of expression would fit it?  
This is family-level economic grammar, not exact-ticket logic.

8\. Memory  
What did PPE say before the outcome?  
This layer freezes the evaluation, preserves version identity, and creates witnessable history.  
Without this layer, the upper stack risks becoming theater.

9\. Review  
What happened later, and how should that be interpreted?  
This is the anti-delusion layer.  
It determines whether the case is supportive, contradictory, contaminated, or unresolved.

10\. Learning / promotion  
What classes deserve to move up or down in trust?  
This layer converts isolated reviewed cases into class-level knowledge.  
It is the beginning of real edge formation.

11\. Operational product  
How does a human actually use this repeatedly?  
This layer includes repeated workflow, saved cases, visibility surfaces, and operator usability.  
It is the shell that makes the inner system usable.

12\. Commercialization  
How does this become sellable, scalable, and positionable?  
This includes packaging, pricing, customer segmentation, and customer-facing wrapper logic.  
It is downstream of the core system, not the essence of it.

Canonical summary  
PPE is best understood as a benchmarked market judgment-and-learning stack.  
Its deepest native flow is:  
sense \-\> represent \-\> compare \-\> gate \-\> judge \-\> express \-\> remember \-\> review \-\> learn.  
Prediction products, opportunity searchers, and customer wrappers may all emerge from this stack, but they are downstream manifestations rather than its deepest identity.

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
\- closest to current product language  
\- easiest to make legible  
\- easiest to explain  
\- easiest to map into expression families  
\- lowest conceptual jump from the current state

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
\- which horizon is being judged  
\- which venue or data source defines the market input  
\- which strike region or convention is being used  
\- which reference the width is being judged against  
\- whether the disagreement is ATM width, term width, event-adjusted width, or another named subtype  
\- whether the signal is broad, local, or mixed  
\- whether data quality is high enough to trust the width estimate

Immediate internal subtype split  
Even if product UI still treats width disagreement as one wedge, internally PPE should distinguish at least:  
\- ATM width disagreement  
\- term width disagreement  
\- event-adjusted width disagreement

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
\- it may be within measurement noise  
\- it may be within benchmark uncertainty  
\- it may disappear inside conservative friction assumptions  
\- it may not teach the system anything useful even if it looks interesting

System-based materiality framework  
For MVP1, materiality should be treated as a relationship, not just a raw threshold.

Define:  
\- market width \= W\_m  
\- benchmark width \= W\_b  
\- absolute gap \= G\_abs \= |W\_m \- W\_b|  
\- relative gap \= G\_rel \= |W\_m \- W\_b| / max(|W\_b|, epsilon)

The system should compare the gap to a materiality floor, not to a naked arbitrary number.

Define the materiality floor as:  
M\_floor \= max(N\_measurement, N\_benchmark, N\_execution)

Where:  
\- N\_measurement \= uncertainty in the market-width estimate  
\- N\_benchmark \= uncertainty in the benchmark-width estimate  
\- N\_execution \= minimum gap needed to survive conservative friction assumptions

Then define a materiality ratio:  
M\_ratio \= G\_abs / max(M\_floor, epsilon)

Interpretation  
\- if M\_ratio \< 1, the gap has not cleared the floor of indifference  
\- if M\_ratio is around 1, the case may be watch-only or marginal  
\- if M\_ratio is clearly above 1, candidate promotion becomes more defensible  
\- stronger gaps support confidence only when trust is also strong

MVP1 practical rule  
If PPE cannot yet estimate these floors directly from data, it may use provisional constants, but those constants must be explicitly labeled as temporary v1 proxies rather than earned truths.

Canonical warning  
Fixed numbers are acceptable as placeholders.  
They are not the real logic.  
The real logic is: a disagreement matters only when it is large relative to the uncertainty and friction floors that surround it.

Recommended MVP1 posture  
For MVP1:  
\- keep both absolute and relative gap visible  
\- use trust tier as part of the implied measurement floor  
\- treat low-trust states as increasing the effective floor  
\- keep the floor logic explicit in provenance or verification  
\- avoid pretending that a small clean gap and a large dirty gap mean the same thing

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
\- candidate signal worth inspection  
\- watch only  
\- paper-track setup  
\- acted setup  
\- no-trade

No-trade as a first-class output  
No-trade is not an absence of output.  
It is a valid output class.

Canonical no-trade states should eventually include at least:  
\- no candidate  
\- mixed / unclear  
\- insufficient trust  
\- insufficient materiality  
\- not executable under current conditions  
\- watch only, not act

Preferred interpretation style  
When PPE returns no-trade, it should try to say why in operator-legible terms.  
For example:  
\- the disagreement is too small to matter after frictions  
\- the data quality is not strong enough  
\- the signal is mixed across references  
\- the structure is interesting but not currently executable  
\- trust checks failed

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
\- many anomaly families at once  
\- exact strike optimization  
\- heavy portfolio machinery  
\- strong recommendation language  
\- autonomous execution logic  
\- broad multi-asset expansion before the first wedge is trustworthy  
\- complex ML ranking before the basic loop is stable

Dependency rule  
Build the thing that makes the next thing trustworthy.  
Examples:  
\- build trust filtering before broad scanning  
\- build candidate history before strong profitability claims  
\- build expression families before exact ticket optimization  
\- build review logic before scaling automation  
\- build calibration before broad capital deployment

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
\- a frozen candidate  
\- explicit trust checks  
\- an expression-family rationale  
\- a falsification condition  
\- a review horizon  
\- a bounded risk rule

If yes, the protocol is maturing.  
That still does not mean edge has been proven.

Minimum candidate snapshot schema  
The candidate layer should not mature further without durable candidate snapshots.

Each frozen candidate record should eventually contain at least:  
\- candidate ID  
\- timestamp  
\- underlying / spot snapshot  
\- expiry / horizon  
\- market data source or venue  
\- quote quality / stale status  
\- spread or liquidity status  
\- usable-strikes count or equivalent quality indicator  
\- reference model or benchmark used  
\- benchmark version  
\- market-implied width or comparable market measure  
\- reference width or comparable benchmark measure  
\- disagreement magnitude  
\- anomaly subtype  
\- materiality score or threshold result  
\- trust flags  
\- confidence score  
\- expression family  
\- falsification condition  
\- review horizon  
\- candidate logic / classifier version  
\- operator action state: ignored, watched, paper-tracked, or acted

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
\- bid / ask reality  
\- slippage  
\- stale quotes  
\- thin-market conditions

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
\- the thesis was directionally right  
\- the candidate was economically meaningful  
\- the proposed expression family fit the thesis  
\- the setup survived realistic execution assumptions  
\- the result is clean enough to teach the system something

Outcome definition must exist at three levels

Level 1: Candidate-level outcome  
Question:  
Was the flagged disagreement real, meaningful, and resolved in the expected direction over the chosen review horizon?

Candidate-level success criteria  
A candidate review should eventually ask:  
\- did the disagreement actually exist under clean data?  
\- was it large enough to matter after conservative frictions?  
\- did the market move in the direction implied by the candidate thesis?  
\- did the disagreement compress, persist, or worsen over the review horizon?  
\- was the candidate mixed, noisy, or not judgeable in hindsight because the inputs were weak?

Interpretation  
This level is about thesis quality, not trade construction quality.  
A candidate can be good even if no trade was placed.  
A candidate can also fail even if a lucky trade would have made money.

Level 2: Paper-tracked setup outcome  
Question:  
If the candidate had been expressed using the chosen expression family under conservative assumptions, would the setup have behaved as expected?

Paper-tracked success criteria  
A paper-tracked review should eventually ask:  
\- did the chosen expression family fit the thesis?  
\- would conservative fills still leave the setup economically meaningful?  
\- was the payoff shape aligned with the actual path of market movement?  
\- did the setup hit falsification before the expected thesis resolution?  
\- did the setup produce a positive, neutral, or negative result under the stated review horizon?

Interpretation  
This level is about expression quality and protocol realism.  
It sits between pure candidate logic and real-money execution.

Level 3: Acted-setup outcome  
Question:  
Did a real bounded action behave in a way that validates both the protocol and the economic idea?

Acted-setup success criteria  
An acted review should eventually ask:  
\- was the action taken under the stated rules?  
\- was the setup attributable to a frozen candidate?  
\- did execution stay within expected friction bounds?  
\- did the setup produce the intended kind of payoff behavior?  
\- did the outcome support, weaken, or invalidate the candidate class?

Interpretation  
This level is not just about P\&L.  
It is also about whether the live protocol is clean enough to trust future evidence.

Canonical review buckets  
Every reviewed case should eventually land in one of a small number of buckets.  
Suggested review buckets:  
\- thesis right, expression right  
\- thesis right, expression weak  
\- thesis mixed, expression irrelevant  
\- thesis wrong, expression irrelevant  
\- not judgeable due to bad inputs or poor witnessability  
\- execution-contaminated result

Why this matters  
Without buckets, the system tends to overlearn from lucky wins and underlearn from structurally useful failures.

Minimum review fields  
Each reviewed candidate should eventually record at least:  
\- review date  
\- realized outcome status  
\- thesis outcome bucket  
\- expression outcome bucket  
\- execution realism verdict  
\- falsification hit or not hit  
\- whether the result is clean enough to teach from  
\- short review note

Suggested realized outcome statuses  
Use a small finite set.  
For example:  
\- supportive  
\- weakly supportive  
\- neutral / unresolved  
\- weakly contradictory  
\- contradictory  
\- contaminated / not judgeable

Review-success criteria by maturity stage

Stage A: early candidate-engine stage  
Success means:  
\- candidates are reviewable at all  
\- review horizons are explicit  
\- results can be frozen and revisited honestly  
\- no-trade outcomes are preserved  
This stage is about witnessability and memory.

Stage B: paper-tracked research stage  
Success means:  
\- some candidate classes show better-than-random quality  
\- confidence buckets start to separate outcomes  
\- expression-family choices become more defensible  
\- contaminated cases are identifiable rather than silently absorbed  
This stage is about calibration and pruning.

Stage C: first-dollar protocol stage  
Success means:  
\- real actions can be traced back to frozen candidates and rules  
\- execution friction does not destroy the basic idea  
\- protocol quality is improving  
This stage is about protocol validity, not proof of durable edge.

Stage D: evidence-backed edge stage  
Success means:  
\- repeated reviewed cases in a class show positive expected value after realistic frictions  
\- the class survives different periods without collapsing into narrative luck  
\- the system can distinguish strong classes from weak ones for real reasons  
This stage is about durable evidence.

Canonical warning  
Do not let a single profitable outcome promote a class too quickly.  
Do not let a single losing outcome kill a class too quickly.  
Promotion and suppression should happen at the class level once review density is high enough.

Outcome-definition rule for width disagreement  
For width-disagreement candidates specifically, the review should eventually ask:  
\- was the width disagreement real under the stated benchmark?  
\- did realized movement or subsequent repricing support the claim that the market was too wide or too narrow?  
\- did the disagreement compress in the expected direction within the review horizon?  
\- would a conservative expression-family implementation have behaved as expected?  
\- was the candidate still meaningful after realistic friction assumptions?

Why this is load-bearing  
This is the section that turns PPE from a machine that notices interesting things into a machine that can learn from what it noticed.

Short summary  
A reviewed success is not just "it made money."  
A reviewed success means the thesis, the expression, and the protocol were clear enough that the result can actually teach the system something.

\============================================================  
12\. CURRENT AUDIT  
\============================================================

Repo-truth anchor  
Live MVP1 steering: `docs/SOP/MVP1_FRONTIER.md`. This section summarizes placement as of **2026-05**; if this audit and the frontier diverge, **update this section explicitly** (approved update rule) rather than letting code or chat drift silently.

Current known state summary  
PPE is strongest in market legibility and bounded product reasoning. **MVP1 Phases 1–6 exist at v0 in `src/`** (substrate → width disagreement → digest surfaces → freeze → review → class summary). The project is past “dashboard only,” but **not** an evidence-backed edge engine: review density and calibration on the evidence clock remain early.

MVP1 phase placement (engineering clock)

| Phase | Status (v0) | Repo pointers |
|-------|----------------|---------------|
| 1 — Market + benchmark substrate | substantially present | implied lab verification, benchmark witness on freeze |
| 2 — ATM width-disagreement engine | substantially present | classification via belief-disagreement contract; trust via Breeden gate / degraded paths |
| 3 — Candidate / watch / no-trade surface | **partial** vs §15 | digest + categories (`width_vol`, `directional`, `mixed`); **`primary_output_state` not yet on verification payload** |
| 4 — Snapshot + memory | substantially present (v0) | `frozen_evaluation_store.py`, **Freeze & history** in UI |
| 5 — Review engine | substantially present (v0) | `snapshot_reviews`, finite statuses, review form on reopen |
| 6 — Class summaries | substantially present (v0) | `reviewed_class_summary.py`, **Class summary — reviewed snapshots** |

Parallel track (not MVP1 phase numbering): **Phase 2 charter** — desirability / playability / UX (`docs/SOP/PHASE_2_CHARTER.md`; Sprint 002 wrapped). **Commercial wrapper** remains deferred (charter “Phase 3–class”), not MVP1 Phase 3.

Layer-by-layer status

Market legibility / sensing  
Status: exists now  
Assessment: current strength  
Risk: do not destabilize it while building higher layers

Reference frame  
Status: partial now  
Assessment: lognormal reference + Breeden market-implied visible; benchmark versioning on freeze is v0  
Risk: anomaly language can drift into vibes if benchmark logic stays loose

Anomaly detection  
Status: partial now, with a chosen wedge  
Assessment: width/directional disagreement categories active; not yet full §15 decision surface  
Risk: do not broaden anomaly families yet

Trust and materiality filtering  
Status: partial now  
Assessment: trust gates exist; **named materiality floors (M_floor, M_ratio) not yet implemented** as in §6  
Risk: candidate UX can become persuasive noise

Candidate panel / operator triage  
Status: v0 present, contract gaps remain  
Assessment: Belief vs market glance, verification, candidate strips; MVP1 compact UI default hides strike/ticket chrome  
Risk: surface can look more finished than strict Phase 3 / §15 contract

Expression family mapping  
Status: partial now  
Assessment: family-level hints; correctly constrained  
Risk: do not jump to exact-ticket precision too early

Candidate history / paper-tracking  
Status: **v0 present** (was “missing” in prior audit)  
Assessment: explicit freeze, SQLite persistence, reopen; operator action states not fully modeled  
Risk: low review density on evidence clock, not absence of memory

Review / calibration  
Status: **v0 present**; calibration weak  
Assessment: per-snapshot review with finite statuses; class rollup + operator hint line  
Risk: strong profitability or edge language would outrun truth; review buckets simpler than §11/§15 full set

First-dollar gate  
Status: conceptually present, operationally not yet earned  
Assessment: gated behind review density and execution realism  
Risk: acting before clean reviewed cases

Expansion / breadth / automation  
Status: intentionally delayed  
Assessment: correct to postpone  
Risk: breadth and automation would amplify ambiguity faster than truth

Naming cleanup conclusions  
\- candidate edge is usable, but should stay modest  
\- mispricing is too strong for casual current-tense use  
\- confidence should mean candidate quality, not certainty of profit  
\- judgment engine is acceptable internally but slightly strong for operator-facing language

The real bottleneck  
The main bottleneck is not vision, dashboard legibility, or wedge selection.

The real bottleneck is: **closing the gap between §15 product contract and shipped behavior**, then **running the closed loop in production** (freeze → review → class summary) so the **evidence clock** can move.

Current bottleneck cluster  
\- §15 contract gaps (`primary_output_state`, explicit materiality versioning, fuller frozen-field witness)  
\- trust / materiality / confidence sharpening in operator-facing copy  
\- demo UX + deployment clarity (public demo vs full app)  
\- review density and calibration (evidence clock), not greenfield memory

Recommended next build boundary  
1\. Validate and document the v0 loop (smoke, operator ritual, demo checklist).  
2\. Close highest-leverage §15 gaps without widening scope (decision surface fields, materiality witness).  
3\. Improve demo/full-app UX under Phase 2 charter constraints.  
4\. Accumulate reviewed cases before stronger edge or first-dollar claims.

What should still wait  
\- multiple anomaly families  
\- exact strike optimization (MVP1 default hides; flag restores dev workbench)  
\- heavier portfolio logic  
\- stronger recommendation language  
\- autonomous execution  
\- broad automation claims

Audit conclusion  
PPE is past the pure-dashboard stage and has a **witnessable v0 research loop in code**, but is not yet at the evidence-backed edge stage. Strongest assets: legibility, guardrails, freeze/review infrastructure. Most important work: **honest contract completion, operator validation, and evidence accumulation** — not rebuilding memory from scratch.

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
\- BTC only  
\- exactly one anomaly family only  
\- exactly one subtype first: ATM width disagreement  
\- one explicit benchmark for candidate generation  
\- candidate generation uses the current system reference distribution, not arbitrary operator belief  
\- belief overlay may remain visible, but it does not drive candidate generation in MVP1  
\- market-implied distribution must be trustworthy enough for candidate generation  
\- if the market-implied path is unavailable or too degraded, no candidate may be produced  
\- output state must resolve to exactly one of: candidate / watch only / no-trade  
\- no-trade is first-class  
\- expression mapping is family-level only  
\- no exact strikes  
\- no executable ticket generation  
\- no autonomous execution  
\- the existing implied-lab / dashboard remains the anchor

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
\- no multiple anomaly families  
\- no exact strike optimization  
\- no autonomous execution  
\- no portfolio machinery  
\- no broad scanner  
\- no multi-asset expansion  
\- no ML ranking  
\- no edge-proven language

Phase architecture

Phase 1 — Market \+ benchmark substrate  
Purpose:  
Create the minimum reliable substrate for ATM width-disagreement evaluation.

Must include:  
\- clear BTC market context  
\- explicit benchmark identity  
\- market width and benchmark width on the same horizon  
\- visible trust state  
\- honest degraded-state handling

Done when:  
\- market width is visible  
\- benchmark width is visible  
\- benchmark identity is explicit  
\- trust state is explicit  
\- the system can honestly say it cannot evaluate a candidate yet

Must exclude:  
\- candidate promotion logic  
\- confidence tiers  
\- output decision logic  
\- snapshot persistence  
\- review engine  
\- class summaries

Phase 2 — ATM width-disagreement engine v1  
Purpose:  
Turn the substrate into one narrow classification engine.

Must include:  
\- ATM width gap calculation  
\- absolute and relative gap calculation  
\- materiality logic  
\- trust gating  
\- classification labels:  
  \- market too wide  
  \- market too narrow  
  \- mixed / unclear  
  \- insufficient trust  
  \- insufficient materiality

Done when:  
\- the system can classify a valid run deterministically  
\- the logic is explicit enough to explain  
\- low-trust states do not promote candidates

Must exclude:  
\- rich candidate UX  
\- snapshot persistence  
\- review logic  
\- class aggregation  
\- additional anomaly families

Phase 3 — Candidate / watch / no-trade decision surface  
Purpose:  
Make the classifier operationally legible to the human operator.

Must include:  
\- single primary output state  
\- explanation  
\- confidence tier  
\- expression-family mapping  
\- falsification condition  
\- review horizon  
\- first-class no-trade reasoning

Done when:  
\- the operator can understand the current evaluation in plain language  
\- candidate / watch / no-trade is explicit  
\- the dashboard remains the anchor

Must exclude:  
\- snapshot persistence  
\- review screens  
\- class learning summaries  
\- exact strategy selection

Phase 4 — Snapshot \+ memory layer  
Purpose:  
Freeze outputs before outcome.

Must include:  
\- explicit freeze action  
\- durable snapshot persistence  
\- retrieval of frozen cases  
\- benchmark version capture  
\- classifier version capture

Done when:  
\- the operator can freeze candidate / watch / no-trade evaluations  
\- frozen records persist and can be reopened  
\- later review is possible because witnessability exists

Must exclude:  
\- full review engine  
\- class-level analytics  
\- auto-logging every UI change

Phase 5 — Review engine  
Purpose:  
Review frozen cases later under explicit outcome criteria.

Must include:  
\- review-horizon handling  
\- candidate-level review  
\- realized outcome status  
\- supportive / contradictory / contaminated logic  
\- review notes  
\- lightweight family-level paper-tracking support if feasible

Done when:  
\- a frozen case can be reopened and reviewed  
\- review statuses are finite and explicit  
\- contaminated / not judgeable is supported

Must exclude:  
\- real-money execution logic  
\- full ticket-level paper-trade engine  
\- class-level decision automation beyond basic summaries

Phase 6 — Class-level learning summaries  
Purpose:  
Aggregate reviewed cases into usable research feedback.

Must include:  
\- counts by direction  
\- counts by confidence  
\- counts by trust  
\- counts by benchmark version  
\- counts by classifier version  
\- simple continue / refine / suppress / retire summary

Done when:  
\- the system can summarize reviewed ATM-width cases at class level  
\- the operator can see whether the class is getting stronger or weaker as evidence accumulates

Must exclude:  
\- automated live capital deployment  
\- broad anomaly scanning  
\- strategy optimization  
\- portfolio / risk engine

Delegation rule for later planning  
At the product level, PPE defines:  
\- the MVP chain  
\- the phase boundaries  
\- the phase done conditions  
\- the anti-scope-creep rules

At the implementation level, the coding agent may define:  
\- slices inside phases  
\- technical implementation order  
\- validation design  
\- repo-specific architecture choices

\============================================================  
14\. PRODUCT GOVERNANCE CONTRACT  
\============================================================

Output-state precedence  
MVP1 must resolve the primary output state in this order:  
1\. invalid market-implied path or invalid benchmark path \-\> no-trade  
2\. low-trust state \-\> no-trade  
3\. mixed / unclear disagreement \-\> watch only or no-trade  
4\. insufficient materiality \-\> no-trade  
5\. marginal but valid disagreement \-\> watch only  
6\. clear, material, high-trust disagreement \-\> candidate

Data-quality taxonomy  
Use three canonical data-quality states:  
\- usable  
\- degraded  
\- invalid

Allowed behavior by quality state:  
\- usable \-\> candidate / watch only / no-trade  
\- degraded \-\> watch only / no-trade  
\- invalid \-\> no-trade only

Interpretation  
Usable means candidate logic is allowed.  
Degraded means the run may still be informative, but should not be promoted confidently.  
Invalid means the run is not trustworthy enough to evaluate honestly.

Benchmark and versioning contract  
Every frozen evaluation should be attributable to explicit product logic versions.  
Minimum required versioning fields are:  
\- benchmark ID  
\- benchmark version  
\- candidate logic / classifier version  
\- materiality-rule version  
\- review-rule version  
\- expression-mapping version

Canonical rule  
If logic changes over time, old cases must remain attributable to the logic version that created them.  
Do not silently rewrite history by letting newer logic blur older cases.

Review-horizon defaults  
MVP1 review-horizon defaults are:  
\- the default review horizon is the selected expiry / horizon active when the evaluation was frozen  
\- frozen cases keep the horizon they were born with  
\- later benchmark or UI changes must not retroactively rewrite old frozen cases  
\- custom multi-horizon review logic is later scope, not MVP1 scope

Why this matters  
Without frozen horizon identity, review quality becomes mushy and hindsight-driven.

Authority rule  
This master document is authoritative for:  
\- product logic  
\- MVP scope  
\- phase boundaries  
\- done conditions  
\- anti-scope-creep rules

The coding agent may decide:  
\- slice decomposition  
\- technical architecture  
\- file/module boundaries  
\- validation implementation

The coding agent may not decide without explicit approval:  
\- to broaden anomaly scope  
\- to promote exact-ticket logic into MVP1  
\- to weaken no-trade as a first-class output  
\- to move autonomous execution forward  
\- to reinterpret the benchmark contract or review contract materially

Canonical summary  
The coding agent owns implementation.  
It does not own product reinterpretation.

\============================================================  
15\. MVP1 PRODUCT BEHAVIOR CONTRACT  
\============================================================

Purpose  
This section defines MVP1 at the product-behavior level so the coding agent does not need to infer operator flow, state behavior, or field-level expectations.

MVP1 user story  
As an operator, I want to open the PPE BTC implied lab, select a single horizon, see whether market ATM width is wider or narrower than the system benchmark, understand whether the disagreement is trustworthy and material, get a candidate / watch / no-trade result with a reason, freeze that result, and later review whether it held up.

Primary product promise  
MVP1 does four things cleanly:  
1\. evaluate  
2\. explain  
3\. freeze  
4\. review

Canonical simplicity rule  
MVP1 evaluates one currently selected BTC horizon at a time.  
It is not yet a scanner across many expiries.  
It is not yet a multi-anomaly engine.

Exact user flows

Flow A — Live evaluation  
1\. Operator opens the BTC implied lab.  
2\. Operator selects one horizon / expiry.  
3\. System shows current market context and trust context.  
4\. System computes market width, benchmark width, gap, trust state, materiality verdict, classification, and output state.  
5\. System displays one primary output: candidate / watch only / no-trade.  
6\. Operator may optionally freeze the current evaluation.

Flow B — Freeze evaluation  
1\. Operator clicks Freeze evaluation.  
2\. System stores a frozen record of the current run.  
3\. Frozen record receives a unique ID and preserves the active review horizon.  
4\. Frozen record can later be reopened for review.

Flow C — Later review  
1\. Operator opens a frozen record after or near the review horizon.  
2\. System shows the original frozen state and the later reviewed state.  
3\. A review result is assigned under the explicit review contract.  
4\. The reviewed case becomes part of class-level summaries.

Exact scope simplification for MVP1  
\- one asset: BTC  
\- one selected horizon at a time  
\- one benchmark only  
\- one anomaly subtype only: ATM width disagreement  
\- one primary output state only per run  
\- one freeze action per chosen run  
\- candidate-level review required  
\- class-level summary required

Exact width basis for MVP1  
For MVP1, use the existing 1σ move width framing already present in the product.

Definitions  
\- market width \= market-implied 1σ move width at the selected horizon  
\- benchmark width \= reference-distribution 1σ move width at the same horizon  
\- absolute gap \= market width \- benchmark width  
\- absolute gap magnitude \= |market width \- benchmark width|  
\- relative gap \= |market width \- benchmark width| / max(|benchmark width|, epsilon)

Canonical rule  
Do not invent a new width definition for MVP1.  
Use the current product’s width framing consistently.

Exact live display contract  
For a live evaluated run, MVP1 should display at minimum:  
\- selected horizon  
\- market width  
\- benchmark width  
\- absolute gap  
\- relative gap  
\- data-quality state: usable / degraded / invalid  
\- materiality verdict  
\- classification label  
\- primary output state  
\- confidence tier  
\- expression family  
\- falsification condition  
\- review horizon  
\- short explanation text

Allowed classification labels for MVP1  
\- market too wide  
\- market too narrow  
\- mixed / unclear  
\- insufficient trust  
\- insufficient materiality

Allowed primary output states for MVP1  
\- candidate  
\- watch only  
\- no-trade

Allowed expression-family outputs for MVP1  
\- short-vol family  
\- long-vol family  
\- watch only  
\- no expression / no-trade

Exact explanation contract  
Every live evaluation should answer four questions in plain language:  
1\. What did the system compare?  
2\. What did it find?  
3\. Why is the result or non-result meaningful or not meaningful?  
4\. Why did it output candidate / watch only / no-trade?

Example explanation patterns  
\- Market ATM width is materially above benchmark width at the selected horizon. Substrate quality is usable. The disagreement clears the current materiality floor, so this run is classified as a candidate with short-vol family bias.  
\- Market ATM width is above benchmark width, but the gap is only marginal relative to the current materiality floor. This run is watch only rather than candidate.  
\- The market-implied path is too degraded to evaluate ATM width disagreement honestly at the selected horizon. This run is marked no-trade due to insufficient trust.

Freeze behavior contract  
Freeze must be explicit and operator-triggered.  
MVP1 should not auto-log every transient rerender.

Freezeable states  
\- candidate  
\- watch only  
\- no-trade

Why this matters  
The system must remember not only interesting candidate cases but also suppressed and no-trade cases, or learning becomes action-biased.

Exact frozen-record contract  
Each frozen record must contain at minimum:  
\- frozen record ID  
\- timestamp  
\- underlying  
\- selected horizon  
\- market data source / venue  
\- data-quality state  
\- benchmark ID  
\- benchmark version  
\- candidate logic / classifier version  
\- materiality-rule version  
\- review-rule version  
\- expression-mapping version  
\- market width  
\- benchmark width  
\- absolute gap  
\- relative gap  
\- classification label  
\- primary output state  
\- confidence tier  
\- expression family  
\- falsification condition  
\- review horizon  
\- operator action state: ignored / watched / paper-tracked / acted

Exact review contract for MVP1  
MVP1 requires candidate-level review.  
Paper-tracked expression review may remain lightweight.  
Acted-setup review is later scope.

Candidate-level review question  
Did the ATM width disagreement move in the expected direction by the frozen review horizon under the same benchmark framework?

Required review outputs  
\- supportive  
\- weakly supportive  
\- neutral / unresolved  
\- weakly contradictory  
\- contradictory  
\- contaminated / not judgeable

Required review fields  
\- review date  
\- current reviewed comparison at review time  
\- review status  
\- whether disagreement compressed / persisted / worsened  
\- clean enough to teach from: yes / no  
\- short review note

Class-level summary contract for MVP1  
MVP1 class summaries should aggregate by at least:  
\- direction: too wide / too narrow  
\- confidence tier  
\- data-quality state  
\- benchmark version  
\- classifier version  
\- review outcome status

Minimum class-level outputs  
\- total reviewed count  
\- supportive count  
\- neutral count  
\- contradictory count  
\- contaminated count  
\- simple verdict:  
  \- continue  
  \- refine  
  \- suppress  
  \- retire

Explicit out-of-scope list for MVP1 product behavior  
\- evaluating many expiries at once  
\- broad scanning behavior  
\- multiple anomaly families  
\- term-width engine as a separate classifier  
\- skew / peak / calendar classifier families  
\- exact strike selection  
\- ticket construction  
\- position sizing  
\- portfolio/risk engine  
\- autonomous execution  
\- multi-asset behavior  
\- ML ranking

Canonical summary  
MVP1 is one-screen BTC ATM-width evaluation with freeze-and-review.  
It should tell the operator what the current state is, what to do with that state, let them freeze it, and let them review it later without ambiguity.

\============================================================  
15A\. MVP1 IMPLEMENTATION STATUS (REPO-TRUTH)  
\============================================================

Purpose  
Maps §15 product contract to what exists in `src/` today. **Target spec remains §15**; this section prevents audit drift. Update when freeze/review/decision payloads change materially.

| Contract element | Status | Notes |
|------------------|--------|--------|
| Freeze explicit, operator-triggered | **shipped (v0)** | `build_frozen_evaluation_record`, **Freeze & history** |
| SQLite persistence + reopen | **shipped (v0)** | `PPE_SNAPSHOT_DB_PATH`, `frozen_evaluation_store` |
| Benchmark + classifier version on freeze | **shipped (v0)** | `benchmark_witness`, `classifier_version` in frozen JSON |
| Per-snapshot review + finite statuses | **shipped (v0)** | `pending`, `supportive`, `contradictory`, `contaminated`, `not_judgeable` |
| Class-level summary | **shipped (v0)** | `reviewed_class_summary.py`; continue/refine/suppress-style hint |
| `primary_output_state` (candidate / watch_only / no_trade) | **not shipped** | UI uses `disagreement_category_id` + digest copy |
| Data-quality enum (usable / degraded / invalid) | **partial** | Trust via Breeden skip, belief invalid, degraded copy — not §14 enum on payload |
| Materiality floors (M_floor, M_ratio) | **not shipped** | Canon in §6; thresholds live in disagreement helpers only |
| Full §15 frozen top-level fields | **partial** | Full `verification` blob stored; not all §15 fields denormalized |
| MVP1 compact UI (hide strikes/ticket) | **shipped** | `PPE_POST_MVP1_LAB_UI` |
| Demo vs full app CTA | **shipped** | `PPE_ENABLE_SNAPSHOTS`, `PPE_PRIVATE_APP_URL` |

Canonical rule  
“Substantially present” in `MVP1_FRONTIER.md` means **v0 landed**, not **§15 complete**.

\============================================================  
16\. FINAL SUMMARY  
\============================================================

What PPE most needs right now  
PPE does not mainly need more intelligence right now.  
It needs:  
\- stronger benchmark definition and materiality witness on the payload  
\- **use** of the existing freeze/review loop in real operator and demo workflows  
\- stronger review discipline and evidence-clock density  
\- stronger execution realism before edge claims

Project-level coherence verdict  
The project is coherent.  
No major conceptual pivot is needed.  
The main need is not category change.  
It is disciplined progression.

Master one-sentence summary  
PPE is a human-centered BTC volatility / relative-value research cockpit that should evolve into an auditable edge-research system by making market structure legible, surfacing candidate disagreements, filtering them honestly, remembering what it said, and learning over time which setup classes deserve promotion.

Short summary  
Keep the vision.  
Keep the dashboard.  
Keep the first wedge narrow.  
Formalize the benchmark.  
Make candidate outputs honest.  
Remember them.  
Review them.  
Then earn stronger claims.

