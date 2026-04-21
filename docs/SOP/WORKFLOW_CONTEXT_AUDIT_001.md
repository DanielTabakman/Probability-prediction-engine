# Workflow Context Audit 001

**Status:** canonical record (first entry in the `WORKFLOW_CONTEXT_AUDIT_*` series).
**Plane:** CONTROL-PLANE. **Posture:** **advisory, not gating.**
**Scope anchor:** `docs/SOP/CURRENT_FRONTIER.md` "Current feature slice" (`Workflow-Hardening-Slice-001`, SELECTED 2026-04-21).
**Cross-refs:** `docs/SOP/SPRINT_003_PHASE_2.md` §6.A + §9; `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md` (runtime-health / Cursor-turnaround vocabulary); `docs/SOP/WORKFLOW_METRICS_V1.md` (companion metric surface — this audit does **not** amend it).

---

## 1. Purpose

Record, in one place, the timing/context audit signal that surfaced during **Sprint003-Slice001** (the first real relay-assisted BUILD, closed 2026-04-21 under §15 `CONTINUE` / `rule_matched == "15.2 rule 7"`), and convert that one-off observation into a **persistent, lightweight advisory surface** — threshold bands + heuristics + actions — that the steward can consult before any future BUILD pass.

This doc is **advisory**:

- It does **not** introduce a new pass/fail gate.
- It does **not** add a new enum value to `WORKFLOW_METRICS_V1.md`.
- It does **not** amend `CODEX_AUTONOMY_V1.md`, `JOB_REGISTRY_V1.md`, or `RELAY_RUNTIME_V0.md`.
- It does **not** change execution-step discipline (`OPERATING_RULES.md`) or the steward workflow (`FRONTIER_STEWARD_PROTOCOL.md`).

If a future slice wants any of those to become **gating**, that requires its own explicit SELECTION and BUILD.

---

## 2. Audit grounding (what was observed)

**Audited pass:** `Sprint003-Slice001` end-to-end (CONTROL-PLANE SELECTION → EVIDENCE-PLANE BUILD via `run_selected_slice_v1` → `§14.1` payload → `§15` decision `CONTINUE` → steward CONTROL-CLOSEOUT). Evidence pointers already recorded in `SPRINT_003_PHASE_2.md` §9 (`artifacts/relay/runs/20260421_163438/*`, `artifacts/health/20260421_164325/control_plane_consistency_report.json`, pytest 117 passed).

**Observations (qualitative, first-pass — not a formal measurement study):**

1. **Per-pass SOP read count was high.** A single BUILD pass comfortably loaded `CURRENT_FRONTIER.md`, `HANDOFF.md`, `SPRINT_003_PHASE_2.md`, `RELAY_RUNTIME_V0.md`, `CODEX_AUTONOMY_V1.md`, `JOB_REGISTRY_V1.md`, and portions of `FRONTIER_STEWARD_PROTOCOL.md` / `OPERATING_RULES.md` before writing a single line of code. That is a legitimate cost of the relay-governed workflow, but it sits near the workable ceiling for one context window.
2. **Handoff-payload size was large relative to slice size.** The steward packet, acceptance spec, and §14.1 / §15 evidence fields together consumed materially more context than the actual diff (`scripts/relay_runtime_v0.py` step 3 + two unit tests). The *governance overhead : diff size* ratio was high.
3. **Roundtrips per slice stayed within budget, but with little headroom.** The slice cleared end-to-end with no `BLOCKED` decision and `retry_count == 0`, but a second retry or a significant scope expansion would have risked context-window pressure rather than engineering complexity.
4. **Signal dilution is the first failure mode to expect.** Before the placeholder-literal suppression shipped, `control_plane_consistency_check` surfaced known-benign warnings that themselves consumed steward attention during review — an in-miniature version of the overall context-budget problem.

**Headline finding:** governance/context overhead was **near ceiling, not over** for Sprint003-Slice001. The next best move is to install a small advisory surface that names the bands and actions **before** the next BUILD (Sprint 003 §6.B candidate or a re-charter) potentially pushes the same dimension over.

---

## 3. Threshold bands (advisory)

The bands below describe **per-BUILD-pass context + handoff load**, not validation runtime (`FRONTIER_STEWARD_PROTOCOL.md` "Runtime health indicators") and not Cursor turnaround (`FRONTIER_STEWARD_PROTOCOL.md` "Cursor turnaround health"). They are **judgment-call** bands with concrete lightweight heuristics — the steward picks the band that best matches the current pass.

A pass is classified by the **worst** band any single heuristic triggers (i.e. if one heuristic says WATCH and the rest say NORMAL, the pass is WATCH).

### 3.1 NORMAL

**Meaning:** the pass is comfortably within the workable context budget; governance overhead is proportional to slice size.

**Lightweight heuristics (all hold):**

- Canonical-doc reads for the pass stay at or below roughly **4** `docs/SOP/**` files (e.g. `CURRENT_FRONTIER.md`, `HANDOFF.md`, the active sprint spec, and at most one protocol/runtime anchor).
- Steward handoff payload (the packet sent to the BUILD agent) is at or below roughly **~200** lines of prose/spec.
- Slice scope is **S** (one bounded outcome) or a well-bounded **M** with a single acceptance clause.
- Expected roundtrips for the pass: **≤ 2** (one BUILD, optional one repair).

**Advisory actions:** proceed normally. No special load-shedding. Optional: record the pass in the steward ledger with `context_band: NORMAL`.

### 3.2 WATCH

**Meaning:** the pass is still feasible but governance/context overhead is approaching the workable ceiling. Small additional pressure (a second retry, a scope nudge, an extra cross-reference load) could push it into ESCALATE.

**Lightweight heuristics (any one triggers):**

- Canonical-doc reads approach roughly **5–7** `docs/SOP/**` files.
- Steward handoff payload approaches roughly **~200–400** lines.
- Slice scope is **M** with more than one acceptance clause, or the acceptance spec itself is long.
- Expected roundtrips: **3** (including one planned repair).
- Governance-overhead : diff-size ratio feels high (e.g. the spec + evidence payload dwarfs the expected diff) — the Sprint003-Slice001 pattern.

**Advisory actions:**

- **Prefer LOAD-ON-DEMAND SOP reads** — do not pre-load protocol / registry / runtime-spec anchors unless the pass actually writes to them.
- **Trim the handoff packet** — keep the canonical spec and the acceptance clause; link (do not inline) long cross-references.
- **Cap retries explicitly** — declare `retry_budget_max` at the lower end of the allowed range for the slice.
- **Record the band** — note `context_band: WATCH` + the triggering heuristic in the pass return (ledger / `HANDOFF.md` closeout note).

### 3.3 ESCALATE

**Meaning:** the pass is at or beyond the workable context budget. Proceeding without adjustment materially raises the risk of mid-pass drift, hallucinated state, or a muddled CLOSEOUT.

**Lightweight heuristics (any one triggers):**

- Canonical-doc reads would exceed roughly **7** `docs/SOP/**` files, or require reading multiple runtime/protocol specs in full.
- Steward handoff payload exceeds roughly **~400** lines, or embeds a full SOP doc inline.
- Slice scope is **L** / multi-file / multi-plane, or touches both evidence-plane code and control-plane docs in one pass.
- Expected roundtrips: **≥ 4**.
- A prior pass on the same slice hit `retry_count > 0` **and** the next retry would re-load the full governance context again.

**Advisory actions (pick the smallest that resolves the trigger):**

1. **Split the slice.** The most common correct action: carve the pass into two smaller slices, each independently in NORMAL or WATCH.
2. **Prune the handoff ledger.** Drop historical ledger entries from the steward packet; keep only the current SELECTION, current acceptance, and baseline tip + validation pointers.
3. **Defer the non-essential plane.** If the pass mixes planes, drop the non-essential plane to a later pass (keep the single declared plane per `FRONTIER_STEWARD_PROTOCOL.md` "Plane discipline").
4. **Switch to CONTROL-PLANE interlude first.** If the overhead is driven by doc drift / missing advisory infrastructure, run a short CONTROL-PLANE slice (this doc is an example) to compress the overhead before the main BUILD.
5. **Stop and re-SELECT.** If none of the above apply, stop at SELECTION and re-scope; do **not** push through a BUILD in ESCALATE without an explicit steward decision recorded in `CURRENT_FRONTIER.md`.

---

## 4. Heuristic reference (what to count, roughly)

These are **rough** counts, not machine-measured thresholds. The steward is the interpreter.

| Heuristic | How to count | NORMAL | WATCH | ESCALATE |
| --- | --- | --- | --- | --- |
| Canonical-doc reads (`docs/SOP/**`) | Distinct files opened in the pass | ≤ 4 | 5–7 | > 7 |
| Handoff-packet length | Lines of prose/spec in the packet sent to the BUILD agent | ≤ ~200 | ~200–400 | > ~400 |
| Expected roundtrips | BUILD + planned repairs | ≤ 2 | 3 | ≥ 4 |
| Slice scope size | Planned size label from `WORKFLOW_METRICS_V1.md` | S | M | L or multi-plane |
| Governance : diff ratio | Feel: spec + evidence payload vs expected diff | balanced | spec dwarfs diff | spec + ledger dwarf everything |

A heuristic is **advisory**: if it triggers WATCH but the steward has specific reason the pass is still NORMAL (e.g. the handoff payload is long but mostly a single linked spec), the steward records the reason and proceeds.

---

## 5. How to use this doc

- **On SELECTION of a BUILD-class pass:** the steward reviews the heuristics in §4 against the packet being prepared. If the pass is WATCH or ESCALATE, the steward applies the §3 advisory actions **before** sending the packet.
- **On CLOSEOUT:** the steward may record the observed band (`context_band: NORMAL | WATCH | ESCALATE`) in the closeout note. This is optional and does not change acceptance.
- **On repeated WATCH / ESCALATE:** if two or more consecutive BUILD passes classify as WATCH or one classifies as ESCALATE, the steward should charter a follow-up `Workflow-Hardening-Slice-00N` (e.g. to prune the handoff ledger, split a large doc, or revise the LOAD-ALWAYS map) rather than keep paying the overhead pass-over-pass.

---

## 6. Explicit non-goals

- **Not a gate.** Nothing in this doc blocks BUILD. `FRONTIER_STEWARD_PROTOCOL.md` "BUILD preflight gate" and `CODEX_AUTONOMY_V1.md` §§5–9 remain the authoritative BUILD gates.
- **Not a new metric.** `WORKFLOW_METRICS_V1.md` field sets are unchanged. Any recording of `context_band` is a ledger note, not a required field.
- **Not a philosophy rewrite.** This is a short, single-purpose canonical record; it does not restructure the SOP.
- **Not a workflow-forcing Cursor rule.** The companion `.cursor/rules/context-budget.mdc` is a **load-on-demand advisory** pointer back to this doc.
- **Not a commitment to future bands.** Thresholds are intentionally rough; if a future audit (`WORKFLOW_CONTEXT_AUDIT_002.md`, etc.) refines them, that is a new slice.

---

## 7. Provenance

- **Audit anchor:** `Sprint003-Slice001` closeout (see `docs/SOP/SPRINT_003_PHASE_2.md` §9 and `docs/SOP/CURRENT_FRONTIER.md` "Steering continuity" 2026-04-21 entry).
- **Evidence pointers (pre-existing, not produced by this slice):**
  - `artifacts/relay/runs/20260421_163438/relay_result.json` (relay result payload; `stop_condition == null`, `ready_for_control_closeout == true`).
  - `artifacts/relay/runs/20260421_163438/decision.json` (§15 decision `CONTINUE`, `rule_matched == "15.2 rule 7"`).
  - `artifacts/health/20260421_164325/control_plane_consistency_report.json` (post-BUILD functional witness: `passed: true`, `findings: []`).
  - Pytest baseline at closeout: **117** passed (universal tier, deterministic).
- **This slice (Workflow-Hardening-Slice-001) produces:** this doc; `.cursor/rules/context-budget.mdc`; optionally a ≤ ~20-line LOAD-ALWAYS / LOAD-ON-DEMAND subsection in `FRONTIER_STEWARD_PROTOCOL.md`. No product, runtime, or test changes.
