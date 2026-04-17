# Sprint 001 — Slice 011 (Phase 2) — Guided “Try next” follow-on moves (repeat-play affordances)

Status: **PENDING** (selected; ready for transactional BUILD once preflight allows)  
Scope posture: **layout/copy/affordance-only** (reuse existing valid moves/presets; no semantic-contract changes)

Canonical sprint anchor: `docs/SOP/SPRINT_001_PHASE_2.md`  
Canonical steering ledger: `docs/SOP/CURRENT_FRONTIER.md`

---

## 1) User problem

After a user completes a **first meaningful action** (e.g., uses an existing control or preset and sees the main object change), they may not know what to do next:

- The current loop does not strongly invite **repeat play**.
- The product can feel like it “ends” after the first interaction, even though additional safe interactions exist.

## 2) Slice goal

Make the **second and third interactions** feel:

- **Obvious** (there is a clear next thing to try)
- **Relevant** (it follows from the current view / last action)
- **Low-friction** (one click / one small action)
- **Safe** (clearly exploratory; trust/provenance remains visible)

## 3) UI target (what changes in the UI)

Add **1–3** “Try next” affordances:

- **Placement**: adjacent to the existing **“What changed?” / interpretation** area (same local loop neighborhood).
- **Mapping**: each affordance maps to an **existing valid control or preset** (no new interactions; no new state models).
- **Effect**: each affordance produces a **visible change in the main object** (not just secondary chrome).
- **Meaning refresh**: each affordance causes the **plain-English meaning readout** to refresh (the same “what changed?” mechanism, reflecting the new last action).

Notes:

- The affordances are **not** a new system; they are a small UI bridge into **already-supported** interactions.
- The affordances must remain **bounded**: at most **three** options, and only those that reliably produce a visible main-object change.

## 4) Tone / contract constraints

The slice must preserve Phase 2’s exploration boundary:

- **Descriptive exploration only** (no “you should”, no “best”, no “recommended”, no “optimal”).
- **Suggest the interaction, not the conclusion** (invite a click/action; do not assert what the user will “learn” or what is “better”).
- Keep **trust/provenance visible** (do not hide verification/provenance paths; do not demote them beyond the current accepted baseline posture).
- No semantic-contract changes; wording stays aligned with `docs/SEMANTIC_CONTRACTS.md`.

## 5) Anti-goals (explicitly not in this slice)

- No recommendation engine (no ranking/scoring logic; no personalization).
- No tutorial tree / guided lesson flow.
- No new calculations, models, or derived metrics.
- No hidden logic (no opaque “because you did X…” inference system).
- No spammy/generic prompts (“Try everything”, “Explore more”, etc.).
- No more than **1–3** suggestions at a time.

## 6) Acceptance checklist (for BUILD)

- [ ] There are **1–3** clear follow-on affordances (“Try next”).
- [ ] They are **adjacent** to the existing loop (near “What changed?” / interpretation).
- [ ] They **reuse existing valid interactions** (controls/presets already supported).
- [ ] Each produces a **visible main-object change** **and** an **updated meaning readout**.
- [ ] Wording stays **descriptive-only** (no recommendation language).
- [ ] Trust/provenance remains **visible** (no new hiding/demotion beyond accepted baseline).
- [ ] Result feels like an **invitation**, not an instruction.

## 7) Validation plan (for later transactional BUILD)

Tier policy: **Tier 1 only** for this slice.

- **Cheap unit tests (if applicable)**: only if any pure helper is introduced for assembling these affordances (e.g., mapping to existing actions). If none are introduced, no new unit tests are required.
- **Primary smoke A**: run the repo’s primary UI smoke (no new scenario tax implied by this doc).
- **Manual / screenshot check**: capture one manual check (or screenshot) showing:
  - the “Try next” affordances present beside the interpretation area, and
  - one affordance clicked → main object visibly changes → meaning readout refreshes.

## Reproducibility caveat (lightweight)

Some environments may have an **accepted local baseline branch** that is **not present on `origin` by name**. Treat the **commit SHA** (and canonical docs) as the source of truth for reproducible starting state; do not assume a branch name exists remotely.

