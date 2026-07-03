# Factory change coordination v1

**Plane:** CONTROL-PLANE · **Audience:** operators, IDE BUILD agents, stewards  
**Purpose:** Coordinate **building new autobuilder / factory surface** — not operating the live pipeline.

**Related:** [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) (whether) · [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) (runtime layer sync) · [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) (run/diagnose) · [`MULTI_AGENT_WORKER_INTERFACE_V1.md`](MULTI_AGENT_WORKER_INTERFACE_V1.md) (leases) · [`DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md`](DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md) (phased rollout template)

**Discovery:** `python scripts/resolve_sop.py --topic "factory change" --json`

---

## Scope split (do not confuse)

| Doc | When |
|-----|------|
| **This doc** | Adding/changing factory code: phases, `direct_action`, status fields, dispatch, agents |
| [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) | Product already on `main` but factory bookkeeping lags (markers, closeout registry) |
| [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) | Gate on **whether** meta-infrastructure is grounded |

---

## Change tiers

Use the tier to size the slice, lease scope, and verification bar.

| Tier | Scope | Typical touch | Lane | Verification |
|------|--------|---------------|------|--------------|
| **F0** | Doc-only | SOP, agent `.md`, routing table | Any | Link check + gate tier 0 |
| **F1** | Local script + test | One `scripts/ppe_*.py`, matching `tests/` | `codex-app` on `control-plane/*` | Targeted pytest + gate |
| **F2** | SSOT wiring | `ppe_operator_status`, `ppe_burst_plan`, `ppe_coordination_check`, button map | `codex-app` + lease on all F2 paths | Status write + coordination check + burst tests |
| **F3** | VM loop behavior | Watch/loop/ntfy on loop host | F2 + **deploy note** in slice | `ppe_autobuilder.cmd diagnose` after VM `git pull` |
| **F4** | New agent / rule surface | `.cursor/agents/*`, `.cursor/rules/*`, `AGENT_ROUTING_V1` | Steward SELECTION + F2 bar | Full operator smoke + `resolve_sop --list-topics` |

**Default:** ship the **smallest tier** that solves the pain. Do not jump F1 → F4 in one slice.

---

## Intake (before coding)

1. **Grounding** — cite which [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) purpose **(a–e)** the change serves. If none → defer or steward SELECTION.
2. **Intake path** — factory features are not drive-by script edits:
   - Product-linked factory work → `ppe_request.cmd --chapter-id …` when it affects relay queue.
   - Pure meta → steward note or control-plane IDE BUILD starter; never hand-edit `PHASE_QUEUE.json` / `ACTIVE_PHASE_MANIFEST.json` ([`CONTROL_PLANE_OPERATOR_V1.md`](CONTROL_PLANE_OPERATOR_V1.md)).
3. **Thread role** — implement in **IDE BUILD** (control-plane starter), not operator `what's next?` thread ([`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)).
4. **Lease** — `python scripts/ppe_worker_lease.py --acquire --worker codex-app --branch control-plane/<slice> --paths …` before F1+ ([`MULTI_AGENT_WORKER_INTERFACE_V1.md`](MULTI_AGENT_WORKER_INTERFACE_V1.md)).
5. **Tier pick** — record F0–F4 in starter or commit message.

---

## Touch-surface checklist (by change type)

| Change type | Must also update |
|-------------|------------------|
| New autobuilder **phase** | Phase enum in status writer, `ppe_autobuilder*.py`, `@ppe-autobuilder-operator` table, diagnose report, tests |
| New **`direct_action`** | `ppe_burst_plan.py`, `ppe_operator_dispatch.py` (when present), [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) |
| New **status / ROOT CAUSE field** | `ppe_operator_status.py` formatter, `CONTROL_PLANE_STATUS.json` reconcile, founder surface if user-visible |
| New **coordination rule** | `ppe_coordination_check.py`, [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) issue codes, gate warn list |
| New **canonical command** | [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) — do not invent parallel `.cmd` paths |
| New **subagent** | [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md), forbid overlap with existing agents ([`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md)) |
| New **topic route** | `scripts/sop_discovery_core.py` `TOPIC_ROUTES`, [`test_sop_topic_coverage.py`](../../tests/test_sop_topic_coverage.py) phrase |

---

## Machine boundary

Per [`.cursor/rules/ppe-desktop-vm-layout.mdc`](../../.cursor/rules/ppe-desktop-vm-layout.mdc):

| Host | Runs |
|------|------|
| **VM loop host** | `run_ppe_auto_local_loop`, watch, ntfy listeners, `run_ppe_local` |
| **Desktop** | IDE BUILD, `DESKTOP_BUILD` / `DESKTOP_CONTINUE`, burst / director |

Every F3+ slice must state in the starter:

- **Deploy:** VM `git pull` required? Desktop-only?
- **Opt-in:** env flag default **off** when behavior is new or noisy ([`DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md`](DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md) pattern).

---

## Phased rollout (mandatory for F2+)

Copy the automation plan shape:

1. **Goal** — one sentence + acceptance criterion
2. **Step N** — code + tests; ship incrementally when possible
3. **Opt-in** — `PPE_*=1` or `--flag`; default off until proven
4. **Verify** — commands block (below)
5. **Manual fallback** — what still works if flag is off

Reference implementation: [`DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md`](DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md).

---

## Verification gate (before merge)

**F1 minimum:**

```bat
python -m pytest tests/test_<relevant>.py -q
python scripts/run_pushable_gate.py
```

**F2+ add:**

```bat
python scripts/ppe_coordination_check.py --write --json
python scripts/ppe_operator_status.py --write
python -m pytest tests/test_ppe_burst_plan.py tests/test_ppe_operator_status.py -q
```

**F3+ add (after VM pull on loop host):**

```bat
ppe_autobuilder.cmd diagnose
ppe_autobuilder.cmd status --write
```

**Never merge F2+** with only script changes — if burst/status/coordination consumers changed, their tests and docs must move in the same PR.

---

## Parallel factory work

[`PARALLEL_AGENT_CHECKLIST_V1.md`](PARALLEL_AGENT_CHECKLIST_V1.md) covers product layers. For factory:

| Rule | Why |
|------|-----|
| One factory slice per branch | `ppe_operator_status` + `ppe_burst_plan` conflict easily |
| Disjoint `ALLOWED_PATHS` | Or separate worktrees |
| Serial merge to `main` | VM pulls once; avoid half-old burst routing |
| Operator thread = SRE only | `@ppe-autobuilder-operator` diagnoses; `@ppe-build-worker` implements |

---

## Thread → agent map

| Thread | Builds factory? | Agent |
|--------|-------------------|-------|
| Operator (`what's next?`) | **No** — run/diagnose | `@ppe-director`, `@ppe-autobuilder-operator` |
| IDE BUILD + control-plane starter | **Yes** | `@ppe-build-worker` |
| Charter / explore | **No** — park | One-line pointer to operator thread |
| Coordination uncertain | **No** — audit first | `@ppe-coordination-check` |

---

## Roadmap tiers (future factory programs)

Deferred programs — enable only when triggers fire twice ([`MULTI_AGENT_ROADMAP_V1.md`](MULTI_AGENT_ROADMAP_V1.md) pattern).

| Tier | Program | Trigger to start |
|------|---------|------------------|
| **FC-1** | Central dispatch executor | Step 2 of desktop automation plan — `ppe_operator_dispatch.py` |
| **FC-2** | Factory change linter | Repeated F2 merges missing burst/status updates |
| **FC-3** | `ppe_factory_change_audit.py` | Pre-merge checklist enforced in gate (F2 touch-surface) |
| **FC-4** | VM/desktop config split | Same script behaves differently per host without env docs |
| **FC-5** | Factory slice starters | `IDE_BUILD_STARTER_Factory-*.md` template from phase plan |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-03 | v1 — factory BUILD coordination SSOT |
