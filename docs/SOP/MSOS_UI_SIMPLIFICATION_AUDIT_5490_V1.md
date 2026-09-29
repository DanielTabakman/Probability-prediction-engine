# MSOS UI simplification audit — #5490

**Status:** Audit and design only. No UI implementation in this pass.  
**Issue:** [#5490](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5490)  
**Parent:** #5488  
**Baseline:** `origin/main` `52fd83a173df0748cc10b5ba5470f731302fa2a6`  
**As-of:** 2026-09-29

This pass inventories the screens a person can open, names the duplicate doors, and proposes one information architecture. It does not change what any number, fit score, or payoff means.

Machine-readable sources used, in this order:

| Source | What it is | Limit |
|--------|------------|--------|
| `apps/msos-web/src/lib/msosPublicUrls.ts` `MSOS_ROUTES` | Named product routes the shell is allowed to link | Omits Options Market Read, `/daniel`, Strategy Lab substeps, and monitor detail routes |
| `apps/msos-web/src/data/commandCenterFixtures.ts` | Primary nav, More nav, launch cards, planned labels | This is the live nav contract |
| `apps/msos-web/src/lib/strategyLabWorkflow.ts` | Compare → Confirm → Plan paper trade | Live stepper |
| App Router `page.tsx` files under `apps/msos-web/src/app/` | What actually renders | Census of user-facing URLs |
| `docs/SOP/PPE_MODULE_REGISTRY_V1.md` | Analytical module table | As-of 2026-06-30. Several rows are behind `main` |

No second module registry is added here.

---

## Current surfaces

### In the app shell

Primary sidebar (`navItems`):

| Label | Route | Question it answers |
|-------|--------|---------------------|
| Command Center | `/command-center` | Where am I, and what should I open next? |
| Strategy Lab | `/strategy-lab` | How does my view compare with the options-implied distribution? |
| Monitor | `/monitor` | What happened to saved views and paper expressions? |
| History | `/history` | What did I record, including reviews? |

More sidebar (`secondaryNavItems`):

| Label | Route | Question it answers |
|-------|--------|---------------------|
| Exposure menu | `/exposure` | What listed paths exist for this asset? |
| Options Horizon | `/options-horizon` | How does implied structure look across price and time, including a drawn region? |
| Forward consistency | `/forward-consistency` | Do related markets agree? Research / ops read. |
| Learn | `/learn` | Session reflection. |

Strategy Lab stepper (`STRATEGY_LAB_WORKFLOW_STEPS`), still inside the shell, active nav stays Strategy Lab:

| Step | Route |
|------|--------|
| Compare view | `/strategy-lab` |
| Confirm view | `/strategy-lab/confirm` |
| Plan paper trade | `/strategy-lab/expression` |

Monitor detail routes, linked from feeds, not from the sidebar: `/monitor/snapshot/[id]`, `/monitor/paper/[id]`.

Feedback inside the shell: `/feedback`. Operator inbox, not a trader destination: `/operator/feedback`.

### Outside the app shell

| Route | What a person sees | Nav |
|-------|--------------------|-----|
| `/` | Public homepage. Primary button is “Start guided tour” into Strategy Lab. Secondary: jump to Strategy Lab, research-beta request, sign in. Feature row adds three more tour variants. | `PublicNav`: Platform, Strategy Lab, Monitor, Command Center, Sign in |
| `/options-market-read` | Own header. “Ask what the options market is pricing.” BTC, informational. | Not in `MSOS_ROUTES` or the sidebar. Help at `/options-market-read/help`. API help at `/options-market-read/api-help` is a distribution note, not a product door. |
| `/daniel` | Personal labs shelf. | Brand link home. Not a trading surface. |

### Module registry versus what is on `main`

| Registry row (2026-06-30) | On this `main` |
|---------------------------|----------------|
| `implied_distribution` → `/strategy-lab`, LIVE | Live. Also the homepage’s default first click. |
| `options_horizon` → `/options-horizon`, LIVE | Live, under More, and also a Command Center card and a Strategy Lab toolbar button. Horizon comparison panel is on this page. |
| `forward_consistency` route marked planned | Route is live under More. |
| `expression_planner` → `/strategy-lab/expression`, LIVE | Live. Expression-fit ranking renders on this page. |
| `exposure_menu` → `/exposure`, LIVE | Live, under More, and also a Command Center card. Exposure links onward to `/strategy-lab/expression`. |
| Workflow surfaces: Command Center, confirm, monitor, history | Live. |
| Options Market Read | Not in the registry. Live as its own page since the human console on this history. |
| Region Bet guided shell | Not a route. Components exist (`RegionBetGuidedShell` and its panels). No page imports that shell. Horizon region draw and the Strategy Lab stepper are the mounted thesis path. |

Historical labels that are no longer the next build: horizon-nav “next”, forward-consistency “planned”, and the June UX backlog’s P1 deep-link chapter. Those behaviors are already on `main`. `/daniel` and the operator feedback inbox stay out of the trader map.

---

## Duplicate and conflicting doors

These are entry conflicts. The underlying reads stay different on purpose.

1. **First click.** Homepage hero, public nav, feature-row tours, Command Center hero, and three Command Center cards all offer a primary-styled next step. Public nav treats Strategy Lab, Monitor, and Command Center as peers.
2. **“What are options saying?”** Three live reads: Options Market Read (plain language, BTC, own chrome), Strategy Lab compare (belief against the implied distribution), Options Horizon (price × time and a region). Command Center presents Lab, Horizon, and Exposure as three equal Live cards, each with a primary button.
3. **Command Center hero.** `resolveHeroPrimary` already picks one href (reviews due, resume a draft, open Strategy Lab, or the calibration link). The same hero then adds Options Horizon and History as extra actions, and the card grid adds three more.
4. **Expression.** Plan-paper-trade is a stepper step. Exposure menu also jumps to `/strategy-lab/expression`. Fit ranking lives on that expression page. The unmounted Region Bet shell repeats compare / expression / save in a second workflow that a visitor cannot open.
5. **Return.** Monitor is primary nav and a public-nav peer. History is primary nav and a Command Center hero link. Learn is a third reflection surface under More.

---

## Five journeys

| # | Journey in #5490 | What works today | Where it breaks |
|---|------------------|------------------|-----------------|
| 1 | Understand what the options market is saying | Options Market Read states one question. Strategy Lab and Options Horizon show richer structure. | The visitor is sent to a belief tour first. The plain-language read is unlisted. Horizon is both “More” and a peer launch card. |
| 2 | Express a market thesis | Strategy Lab stepper: compare, confirm, plan. Horizon can draw a region and link back to the lab. | Region Bet copy exists in unmounted components, so it looks like a second thesis product in the codebase and is invisible in the UI. |
| 3 | Compare ways to express that thesis | `/strategy-lab/expression` shows paper structures and fit ranking. `/exposure` lists paths and can open that same planner. | Exposure is a top-level card and a side path into the same planner. |
| 4 | Inspect evidence and limitations | Lab trust banners, Horizon comparison limitations, Market Read’s “does not recommend a trade” line, Monitor’s last-seen versus now. | Evidence is per tool. No single place tells you which tool’s limits you are reading. |
| 5 | Same capabilities through API or agent clients | Options Market Read has an API-help link. Display boundaries stay in Python (`PPE_MODULE_REGISTRY_V1.md`). | API catalog work is #5492. This audit does not add adapters. The web UI must keep calling those reads rather than recompute them. |

#5491 (full thesis object and saved comparison) is not part of this phase.

---

## Proposed information architecture

One product. Five doors in order. Everything else is disclosure.

**Primary**

1. **Home** (`/command-center`) — one sentence of status, one primary button, resume list.
2. **Read** — Strategy Lab compare (`/strategy-lab`) for belief versus implied distribution. Options Market Read stays available as the plain-language BTC read, linked from More, not as a second home.
3. **Paper** — reached by the existing stepper (confirm, then plan). Not a separate top-level product.
4. **Monitor** — saved views and paper expressions, including last-seen versus now.
5. **History** — record and review.

**More**

Options Horizon, Exposure menu, Forward consistency, Learn, and Options Market Read. Planned labels already in `plannedModules` (Event markets, Perp positioning) stay inside that disclosure.

**Leave in place, unlabeled as trader nav**

`/daniel`, `/operator/feedback`, `/feedback` as a form reached from a session, and `/options-market-read/api-help`.

Public homepage keeps one recommended first step: the guided tour into Strategy Lab. Extra tour variants sit behind one “Other ways to start” disclosure. Public nav stops presenting Monitor as a peer of the first visit.

Financial meanings stay as they are. Fit ranking stays educational. Nothing in this map turns a read into a recommendation or an order.

### Later slices, after the first one is approved

| Order | Slice | Why it waits |
|-------|--------|----------------|
| 1 | Command Center: one next action | Smallest screen that currently shows several primary buttons. Specified below. |
| 2 | Homepage: one start, extra tours disclosed | Same conflict, public entry. |
| 3 | Strategy Lab compare: one primary (“Save your view”); CSV download and Horizon jump behind disclosure | The compare page currently leads with two toolbars. |
| 4 | More-menu link to Options Market Read, using its existing question sentence | Only labeling. Does not merge it into Strategy Lab. |
| — | #5491 read-only thesis workflow | Separate issue. Depends on this map only at its later “integrate with simplified UI” step. |

---

## First bounded slice

**Id:** `msos_command_center_one_next_action_v1`  
**Not started.** Waiting for approval.

### Before → after

**Before.** `/command-center` renders:

- a status hero whose primary label comes from `resolveHeroPrimary`;
- Options Horizon and History as further hero actions (`command-hero-secondary`);
- a `module-card-grid` of three Live cards (Strategy Lab, Options Horizon, Exposure menu), each with a primary-styled CTA;
- a “More modules coming” disclosure that only lists planned names;
- a Resume section.

**After.** The same page renders:

- the same status title, body, and the same single primary href rules (reviews due → calibration href; draft → Strategy Lab; empty → Strategy Lab; otherwise calibration href);
- no second or third primary button in the hero;
- History as a text link, not a button peer;
- no equal Live launch cards;
- Options Horizon, Exposure menu, Forward consistency, and Learn still reachable from the existing sidebar More and from one on-page “More tools” disclosure that uses `secondaryNavItems` hrefs;
- Resume unchanged.

A person landing on Home sees one next action. The other tools remain one disclosure away. No route is deleted. No engine output is reformatted.

### Acceptance criteria

1. The command hero contains one control that uses the primary button class. Its label and href still follow `resolveHeroPrimary`.
2. The page does not render `module-card-grid` or three peer primary CTAs for Strategy Lab, Options Horizon, and Exposure.
3. Sidebar More still links to `/exposure`, `/options-horizon`, `/forward-consistency`, and `/learn`.
4. The on-page disclosure links to those same four routes.
5. History remains linked from Home and from primary nav.
6. Resume, calibration strip, degraded copy, and `DEMO_FOOTER` stay.
7. Focused tests update the old witnesses that require `module-card-grid` and a hero-secondary Horizon button, and assert the single primary plus the More links. Coverage stays; the expected markup changes to this contract.
8. No edits under `src/engine/`, `src/viz/`, display API routes, or Autobuilder.

### Path ownership

Allowed:

- `apps/msos-web/src/components/CommandCenterContent.tsx`
- `apps/msos-web/src/data/commandCenterFixtures.ts` (only if the disclosure should read `secondaryNavItems` instead of duplicating hrefs)
- `tests/test_msos_web_command_center.py`
- `tests/test_msos_web_horizon_nav.py` (the Command Center Horizon assertion only)
- `tests/test_msos_web_storyboard_visual_parity_witness.py` (the `module-card-grid` witness only)

Forbidden for this slice:

- `apps/msos-web/src/app/options-market-read/**`
- `apps/msos-web/src/components/StrategyLabContent.tsx`
- `apps/msos-web/src/components/PublicNav.tsx`
- `apps/msos-web/src/components/HeroSection.tsx`
- Region Bet components
- `src/**` math and display boundaries
- Factory / Autobuilder repos and control-plane queue files
- API catalog and Qatom handoff docs

### Dependencies

- None on #5491.
- None on Factory refill or catalog orders 14–17.
- Options Market Read and #5492 stay untouched. A later slice may link to `/options-market-read`; this slice does not.
- Existing witnesses above must be updated in the same change so the single-primary contract is what CI checks.

### Founder decision

None for this slice. One product concept: Home picks the next step; Read, Paper, Monitor, and History stay in that order; Horizon, Exposure, consistency, Learn, and Options Market Read stay behind More.

A later choice, not required to approve slice 1: whether Options Market Read should become the public “what is the market pricing?” front door in place of the Strategy Lab tour. This audit keeps the tour as the first public step and Market Read as a disclosed plain-language read.
