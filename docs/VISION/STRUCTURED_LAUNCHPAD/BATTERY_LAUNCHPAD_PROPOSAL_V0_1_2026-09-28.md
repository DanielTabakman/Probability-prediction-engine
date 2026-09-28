# Battery Launchpad — Working Product Proposal v0.1

**Date:** 2026-09-28  
**Status:** PROPOSAL / RESEARCH INPUT — NOT AN IMPLEMENTATION CHARTER  
**Engineering OS lane:** Structured Launchpad  
**Backlog class:** Research  
**Related decision packet:** #5494  
**Implementation authorization:** None. Issue #5494 is chartered only as a Research/Incubation decision packet; this document does not authorize sustained implementation.  
**Collaborators:** Daniel Tabakman and Benny  
**Collaborative copy:** Google Doc shared with Benny; this repository copy is the durable snapshot.

## Purpose

Battery Launchpad is a meme-token launch platform where each token is associated with an underlying **pair** and a simple directional expression: **UP, DOWN, or CHAOS**.

Rather than distributing trading fees continuously, a portion of those fees accumulates in a visible reserve called the **Battery**.

The Battery charges as the token trades. Several times per day, movement in the chosen underlying pair determines whether the Battery discharges and how much is distributed to eligible holders.

The goal is to create a stronger reason to hold than ordinary fee-sharing tokens by combining:

- visible accumulated value;
- market-correlated payouts;
- variable/lumpy rewards;
- payouts in meaningful underlying assets;
- anticipation around market events;
- and a self-reinforcing fee-and-attention loop.

This document defines the current concept and major assumptions. It is intentionally **not** yet a hardened mechanism specification.

## Core thesis

Ordinary reward tokens generally distribute fees continuously.

Battery Launchpad asks:

> **Can the same fee stream become substantially more compelling if it is stored and released conditionally around meaningful market movements?**

Instead of:

`trading → fee → continuous reward`

the system becomes:

`trading → fee → Battery charges → underlying market moves → Battery discharges → holders receive payout → attention increases → trading increases → Battery recharges`

We believe this structure may create more anticipation, utility, and reasons to continue holding than a simple continuous reward stream.

The Battery does not necessarily create additional economic value by itself. Its primary function is to change **when, why, and under what conditions value is distributed**.

Additional value may later come from staking, lending, market-making, options, or other strategy modules, but those are not required to prove the core Battery concept.

## The flywheel

The central economic and behavioral loop is:

`Trading volume → trading fees → Battery charges → visible potential payout grows → market event triggers payout → large/interesting holder payout → attention/content/excitement/utility → more holding and/or trading → more trading volume → Battery charges again`

This is the **flywheel**.

The project works particularly well if each turn of the loop strengthens the next one.

The critical behavioral hypothesis is therefore not merely that users tolerate a fee. It is that the value and excitement created by the Battery can generate enough retention and trading activity to help replenish itself.

## Basic product

A creator launches a meme token by making several high-level choices.

### 1. Choose an underlying pair

The underlying is a **paired market relationship**, for example:

- SOL / NVDA;
- SOL / BTC;
- SOL / ETH;
- SOL / TSLA;
- SOL / another tokenized asset.

The pair defines the market relationship around which the Battery operates.

For example, a SOL/NVDA product may collect value through SOL-denominated trading while the Battery acquires or distributes an NVDA-linked asset.

Exactly how the two sides of the pair interact will be formalized later.

### 2. Choose a directional mode

**UP** — designed to reward the specified positive move or relationship in the underlying pair.

**DOWN** — designed to reward the opposite movement.

**CHAOS** — designed to reward sufficiently large movement regardless of direction.

The intent is to give users simple market expressions without requiring them to understand strikes, expirations, Greeks, or options interfaces.

### 3. Choose launch/economic parameters

The creator chooses from platform-approved variables rather than arbitrary unrestricted configuration.

Likely categories include:

- bonding-curve / launch template;
- total fee;
- creator fee;
- platform fee;
- Battery allocation;
- payout frequency;
- payout/discharge aggressiveness;
- drip/overflow settings;
- approved lifecycle/wind-down policy.

Some of these may ultimately become presets or platform-owned invariants instead of creator-selectable values.

## Launch lifecycle

A token follows a basic lifecycle:

`Creator chooses pair + direction + allowed parameters`

→ token launches on a bonding curve  
→ trading begins  
→ fees accumulate  
→ a share of fees charges the Battery  
→ token reaches its graduation threshold  
→ liquidity migrates to the appropriate market/pool  
→ trading and fee collection continue  
→ Battery continues charging and discharging according to its rules  
→ if the underlying becomes invalid or the token winds down, a predefined lifecycle policy activates.

The exact bonding-curve provider and post-graduation venue are implementation decisions to be determined later.

The current preference is to reuse existing infrastructure wherever possible rather than inventing a new exchange or AMM.

## Fee structure

The token may have a relatively high trading fee—for example around 3%—because the fee is the fuel for the Battery and broader reward system.

The total fee may be divided among several destinations:

- Battery;
- creator;
- platform;
- holder/reward mechanisms;
- other approved destinations.

The exact percentages are not yet fixed.

A key design goal is that fees should, where possible, accrue in a useful quote or underlying asset rather than forcing the protocol to continuously sell the meme token.

### Token-2022 / Stonk-style fee direction

The current concept remains interested in Solana Token-2022 and high-fee token mechanics because persistent trading fees are central to the flywheel.

Possible fee mechanisms to investigate include:

- Token-2022 transfer fees;
- launchpad fees;
- AMM/platform fees;
- creator fees;
- combinations of the above.

Stonk is the current reference model for the desired product behavior: high-fee reward tokens where trading activity feeds rewards and payouts may be made in a quote asset such as SOL.

**Important:** “copy Stonk” is currently a product/mechanism reference, not yet a verified technical implementation. The exact on-chain fee path still needs a bounded technical investigation before production architecture is chosen.

## Charge rate

**Battery charge rate is a derived/emergent property, not necessarily a creator setting.**

Conceptually:

`Battery charge rate = trading volume × effective fee rate × Battery allocation`

Example:

- $1,000,000 daily volume;
- 3% effective fee;
- 80% of collected fees to Battery;

produces roughly **$24,000/day** of Battery charging before other costs or adjustments.

The product should calculate and show this after the creator chooses the underlying variables.

Useful derived outputs may include:

- expected Battery charge at $100K / $1M / $10M daily volume;
- estimated payout frequency under historical volatility;
- potential payout under representative market moves;
- reserve survival under historical scenarios.

## Battery

The Battery is a visible reserve associated with the token.

Depending on the product, the Battery may hold:

- SOL;
- the paired underlying asset;
- a tokenized stock such as NVDA;
- stablecoins;
- or a combination of assets.

A SOL/NVDA product could therefore potentially:

`collect SOL → acquire NVDA-linked asset → distribute NVDA-linked asset`

subject to liquidity and implementation constraints.

The Battery should be publicly observable enough that users can understand:

- current Battery value;
- what assets it holds;
- recent charge rate;
- potential payout at different market moves;
- previous discharges;
- remaining reserve.

This visibility is part of the anticipation mechanism.

## Payouts

Payouts may occur **multiple times per day**.

Possible schedules include:

- hourly;
- every 4 hours;
- every 6 hours;
- daily.

For the MVP, fixed approved schedules are preferable to arbitrary timing.

At each payout epoch:

1. the underlying pair's movement is measured;
2. the token's UP/DOWN/CHAOS rule is applied;
3. a payout amount is calculated;
4. platform safety rules limit the maximum discharge;
5. eligible holder weights are calculated;
6. the payout is distributed.

## Market-correlated discharge

The Battery's discharge should be tied deterministically to the underlying market.

Conceptually:

`larger qualifying move → larger payout`

rather than:

`random jackpot → arbitrary payout`

The exact mathematical payout curve is not finalized.

Potential components include:

- minimum payout;
- base payout;
- convexity;
- maximum discharge;
- reserve floor;
- directional conditions;
- volatility normalization.

These parameters should ultimately be constrained by platform safety limits.

## Payout asset

Whenever practical, payouts can occur in the paired underlying asset itself.

Examples:

- SOL/NVDA UP could potentially pay holders in an NVDA-linked asset;
- SOL/BTC DOWN could potentially distribute a BTC-linked asset.

This is an important part of the utility proposition. The holder is not merely receiving more of the meme token; they receive an external underlying asset associated with the market thesis.

## Holder eligibility

Payouts should not simply go to whoever holds the token at one instantaneous snapshot.

The initial mechanism should use **time-weighted holdings**.

Conceptually:

`holder payout = total payout × holder's time-weighted share`

This discourages someone from buying immediately before a known payout, collecting the reward, and instantly selling.

More advanced loyalty or vesting mechanisms may be tested later, but they are not required for the first version.

## Drip / overflow

A Battery may need a mechanism that prevents it from growing indefinitely during periods without large qualifying market moves.

One possible mechanism is a **drip** or overflow payout:

- Battery maintains a minimum reserve;
- above a defined threshold, some excess is periodically distributed;
- large market events still create substantially larger discharges.

This is an open design variable.

## Creator control vs platform invariants

Creators should have meaningful configuration choices, but they should not have unlimited control over the financial rules.

The design principle is:

> **Creators get knobs. The platform owns the safety envelope.**

Possible platform invariants include:

- maximum Battery discharge per epoch;
- minimum Battery reserve;
- permitted payout frequencies;
- permitted underlying assets;
- oracle requirements;
- minimum liquidity requirements;
- anti-sniping rules;
- maximum fee rates;
- wind-down conditions;
- handling of failed/delisted underlyings.

## Underlying failure / liquidation

The system needs an explicit lifecycle policy for situations where an underlying becomes unusable.

Examples:

- stock/token is delisted;
- tokenized asset loses redemption;
- liquidity collapses;
- asset is liquidated;
- oracle becomes unreliable;
- stablecoin depegs;
- underlying protocol fails.

Initial behavior should probably use predefined platform rules rather than arbitrary creator decisions.

Possible lifecycle response:

`underlying becomes invalid → pause new charging/discharges → convert reserve according to predefined policy → distribute or migrate remaining Battery → token becomes inactive/wind-down`

Eventually creators may choose among approved wind-down templates.

## Core assumptions

### 1. Fees can reliably fund the Battery

The desired fee/reward behavior appears feasible based on existing reward-token systems, but the exact technical fee path still needs to be reproduced and verified before production.

### 2. Traders will tolerate relatively high fees

Existing reward-token behavior suggests some users will trade tokens carrying unusually high fees.

High fees may also reduce bundling, some high-frequency behavior, and some arbitrage.

The unresolved question is:

> **What fee level maximizes the Battery flywheel rather than suppressing volume too severely?**

### 3. Lumpy payouts appeal to a meaningful trader segment

Some traders appear to value highly variable outcomes. Battery deliberately concentrates payouts around market events rather than smoothing them completely.

The product does not need every trader to prefer this payoff structure; it needs a sufficiently large segment to find it compelling.

### 4. Market correlation creates utility

A payout tied to an understandable market relationship should be more meaningful than an arbitrary reward.

UP rewards the selected bullish relationship, DOWN the bearish relationship, and CHAOS large movement.

A payout in the paired underlying may strengthen this relationship further.

### 5. Battery economics can remain sustainable

If the Battery discharges too aggressively, it becomes empty and loses its ability to create anticipation.

Therefore:

`charge rate ↔ payout frequency ↔ discharge rate ↔ reserve floor`

must reach a sustainable relationship.

Simulation should determine safe envelopes.

### 6. Time-weighting can meaningfully prevent payout sniping

Instantaneous holder snapshots would allow traders to enter directly before a payout and immediately exit afterward.

Time-weighted balances should align payouts more closely with actual holding behavior.

### 7. The flywheel produces measurable behavioral effects

This is the largest business assumption:

`larger Battery → anticipation → payout event → attention → increased trading/holding → more fees → larger Battery`

The early links are mechanical; the later links are behavioral and ultimately require live testing.

## What the core thesis does not require

The first Battery validation does **not** require:

- options trading;
- a derivatives exchange;
- AI trading;
- a house book;
- market making;
- lending;
- staking;
- complex yield strategies;
- a platform token;
- custom options;
- fully permissionless creator strategies.

These may become later strategy modules.

## MVP concept

The MVP should prove the Battery mechanism, not the entire eventual platform.

### Creator experience

A creator chooses:

- an underlying pair, e.g. SOL/NVDA;
- UP / DOWN / CHAOS;
- an approved launch template;
- a small set of approved economic/Battery parameters.

The interface then shows the resulting derived Battery characteristics rather than asking the creator to set “charge rate” directly.

### Token experience

The token:

1. launches through a bonding curve;
2. trades;
3. collects fees;
4. charges a Battery;
5. graduates to a liquid market;
6. continues collecting fees;
7. evaluates its underlying pair several times per day;
8. distributes qualifying Battery payouts to time-weighted holders.

### Public token page

A token page should eventually expose:

- pair and mode;
- Battery value and holdings;
- current derived charge rate;
- trading volume;
- next payout epoch;
- underlying movement since epoch start;
- potential payout if the epoch ended now;
- recent payouts;
- historical Battery level;
- holder's estimated time-weighted share.

The Battery should feel visibly **charged**.

## Validation approach before hardening

Before building a hardened permissionless launchpad, simulate:

- real market prices;
- historical underlying pairs;
- synthetic/observed token trading volume;
- fee inflows;
- Battery charge;
- repeated intraday payouts;
- time-weighted holder payouts;
- reserve floors;
- different creator configurations.

Market research should run in parallel, especially on existing Stonk/reward-token behavior: which fee levels, reward assets, payout patterns, and token histories correlate with survival, volume, and holder retention.

A small live pilot should follow only after the mechanism appears economically coherent.

## Longer-term platform vision

If Battery works, it becomes **Strategy #1** inside a broader financial-product launch architecture:

`token launch → fee collection → reserve → strategy slot → holder payout / token economics`

Battery occupies the strategy slot first.

Later strategies could potentially include:

- options;
- covered-call systems;
- basis/funding strategies;
- market-neutral strategies;
- index baskets;
- prediction-market strategies;
- AI-managed strategies;
- other programmable financial products.

Battery is the first proof of the architecture, not necessarily the final form of the platform.

## Current working definition

> **Battery Launchpad allows creators to launch meme tokens associated with an underlying asset pair and an UP, DOWN, or CHAOS market expression. Trading fees charge a visible reserve called the Battery. Several times per day, movements in the underlying market determine whether and how much of the Battery discharges to time-weighted holders, potentially in the paired underlying asset itself. The central hypothesis is that accumulated, market-correlated, high-variance payouts create anticipation and utility, producing a flywheel of payouts → attention → trading → fees → Battery recharge.**

## Open questions — intentionally unresolved

These are the questions to resolve with Benny and through bounded research before an implementation charter:

1. **Pair semantics:** precisely what SOL/NVDA, SOL/BTC, etc. mean for trigger calculation, reserve composition, and payout asset.
2. **Fee plumbing:** reproduce the desired Stonk-style fee path; determine the role of Token-2022 transfer fees vs launchpad/AMM/creator/platform fees before and after graduation.
3. **Bonding curve / graduation:** which existing launch infrastructure is the best fit and what changes at graduation.
4. **Payout asset acquisition:** if fees arrive in SOL but payouts are NVDA-linked/BTC-linked/etc., when and how the Battery acquires the payout asset.
5. **Creator variables vs platform invariants:** which controls are creator-selectable, which are presets, and which are hard safety rules.
6. **Discharge formula:** payout curve, payout frequency, maximum discharge, reserve floor, and drip/overflow behavior.
7. **Time-weighted holdings:** exact anti-sniping window and accounting method.
8. **Underlying eligibility:** liquidity/oracle/market-quality requirements for a pair to be permitted.
9. **Underlying failure:** exact wind-down/liquidation behavior.
10. **Flywheel evidence:** whether lumpy payouts actually improve attention, holding, and trading enough to matter.
11. **Market research:** what existing Stonk/reward-token data says about fees, payout assets, volume, survival, and retention.
12. **Real-money readiness:** custody, security, market-integrity, and legal/regulatory questions must be addressed before a funded public launch.

## Next state

**Wait for collaborator feedback. Do not harden or promote yet.**

After Benny responds, update this proposal to v0.2 (or record disagreements), then decide whether to:
- keep researching;
- define a bounded simulation/shadow MVP;
- or explicitly promote a specific item toward implementation.

Until then, this file is a durable concept snapshot only.
