# MANAGER_LOOP

> **Superseded (2026-06):** MVP1/MSOS relay uses [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md), [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md), and `@ppe-director` / IDE BUILD starters — not manager/worker chat loops. **Do not load this doc for steering.** Historical Phase 2 reference only.

Purpose: define the manager agent's role in the feature slice chain.

## Manager stance
Act as **direction keeper**, **frontier updater**, and **stop-condition gate**. Prefer **larger, higher-leverage feature slices** when they remain testable and do not require a blind structural gamble. **Interrupt less**—trust the worker to take a fuller pass inside one feature slice when the objective is clear.

## Manager responsibilities
- Read `ORIGINAL_SPEC.md`, `CURRENT_FRONTIER.md`, and `HANDOFF.md`
- Choose or approve the next feature slice (can be broader than “smallest patch” if verification is credible)
- Create the next `SPRINT_00X.md` using `SPRINT_TEMPLATE.md` when a formal feature slice file is needed
- **Review worker evidence** (commands, results, diffs, app notes)—do **not** rerun everything by default unless evidence is thin or something fails
- Update `CURRENT_FRONTIER.md`
- Decide one of:
  - continue with another feature slice
  - request fixes
  - stop and escalate to human

## Manager decision rules
Prefer feature slices that:
- have **visible** output and clear **acceptance** checks
- move the product **materially** toward `ORIGINAL_SPEC.md` and the current phase goal
- reduce uncertainty where it blocks progress
- can include **local cleanup** as part of the same pass when confidence is high

Avoid feature slices that:
- depend on **unresolved** product ambiguity
- mix **unrelated** UI, semantics, and architecture with no single testable objective
- expand into **new roadmap** territory without human alignment

## Compact slice mode (optional)

When the next slice is **low-risk** and matches **Compact slice mode** in `OPERATING_RULES.md`, you may plan **SELECTION** then **one BUILD** with **integrated closeout** (instead of always requiring a separate **CLOSEOUT** paste) **only** when Tier 1, targeted inspection, and honest doc updates fit in one clean pass per those rules.

## Evidence to review after each feature slice
- files changed
- exact commands run
- tests run and results
- app launch/inspection evidence if relevant
- what was confirmed vs inferred
- cleanup performed
- risks / caveats
- recommended next step

## Stop or escalate when
Stop or escalate on **real** problems, not on pace:
- **failing** verification (tests, smoke, or agreed inspection) without a credible fix path
- **drift** from `ORIGINAL_SPEC.md` or the current phase that the worker cannot reconcile
- **structural mess** (hygiene, coupling, or conflicts) that threatens the next increment
- **unclear convergence**—multiple plausible directions and no crisp acceptance test

Do **not** stop solely because a feature slice was “large” if evidence shows it met the objective and the repo stayed coherent.

## Frontier update rule
The worker may propose updates to `CURRENT_FRONTIER.md`, but the manager decides what becomes the new frontier.
