# Control plane operator v1

**Plane:** CONTROL-PLANE. **Purpose:** one source of truth and one intake path for human work.

Cross-refs: [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md) · [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)

---

## One read path

After any steering change or when status feels stale:

```bat
ppe_request.cmd reconcile
```

**Read only:** `artifacts/orchestrator/CONTROL_PLANE_STATUS.json`

| Field | Meaning |
|-------|---------|
| `committed.phase_plan_path` | Active chapter (from manifest) |
| `committed.first_ready_queue_plan` | Next queue row the relay will use |
| `verdict` / `phase` / `recommended_action` | What to do now |
| `runtime.build.worker` / `runtime.build.handoff_worker` | Headless vs desktop BUILD agent (`cursor-cli`, `codex-cli`, `manual`) |
| `runtime.build.worker_pref` | Config: `ideHandoff.buildWorker` (`auto` \| `cursor` \| `codex` \| `manual`) |
| `alignment.findings` | Drift between manifest, queue, backlog, continuity brief |
| `runtime` | Full autobuilder snapshot |

Do **not** treat `WHATS_NEXT.md`, old `IDE_BUILD_STARTER_*.md`, or `AGENT_CONTINUITY_BRIEF.md` as live steering unless `alignment.passed` is true and manifest matches your intent.

---

## Human work intake (never jump the pipeline)

When you ask to **do something**, route it — do not hand-edit `PHASE_QUEUE.json` or `ACTIVE_PHASE_MANIFEST.json`.

### Build chapter (product / relay work)

```bat
ppe_request.cmd --chapter-id msos_billing_lemon_squeezy_v1 --reason "Lemon Squeezy webhooks after usable demo"
ppe_request.cmd --chapter-id msos_billing_lemon_squeezy_v1 --reason "..." --apply
```

| `action` | Meaning |
|----------|---------|
| **NOW** | Matches active chapter — use `commands` (e.g. `DESKTOP_BUILD.cmd`, `run_ppe.cmd`) |
| **WAIT** | Pipeline busy or blocked verdict — finish current slice first |
| **QUEUE** | Appended to `PHASE_CHAPTER_BACKLOG.json` as `blocked` — relay picks it up when idle |
| **ALREADY_QUEUED** | Already `chartered` / `queued` in backlog |

`--apply` writes the backlog row. Without `--apply`, dry-run only.

**Urgent IRL override:** `--urgent --urgent-reason "demo tomorrow"` bypasses focus gate (see [`ppe_focus_gate.py`](../../scripts/ppe_focus_gate.py)).

### Policy / architecture (not auto-built)

```bat
ppe_request.cmd human --title "Lemon Squeezy operator accounts" --summary "Need Lemon Squeezy store + checkout URL before billing BUILD" --apply
```

Goes to [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) — steward review, not relay.

---

## Layer model

```text
Human idea
  → ppe_request.cmd (route)
      → NOW     → relay / IDE BUILD (when pipeline ready)
      → WAIT    → finish active chapter / fix verdict
      → QUEUE   → PHASE_CHAPTER_BACKLOG.json (blocked)
      → HUMAN   → HUMAN_STEWARD_BACKLOG.json

Relay idle
  → propagate_queue → PHASE_QUEUE READY → manifest
  → run_ppe.cmd slices

Closeout
  → apply_control_closeout_v1 → AGENT_CONTINUITY_BRIEF.md (narrative only)
```

**Committed truth:** `ACTIVE_PHASE_MANIFEST.json` + `PHASE_QUEUE.json` on **`main`**.

**Runtime truth:** regenerate with `ppe_request.cmd reconcile`.

---

## Agent rule

1. `ppe_request.cmd reconcile` (or `ppe_autobuilder.cmd reconcile`)
2. Read `CONTROL_PLANE_STATUS.json`
3. If user asks for new work → `ppe_request.cmd --chapter-id ... --reason ...` (add `--apply` when steward confirms)
4. Never implement off-manifest chapter work in the same pass

---

## Commands

| Command | Role |
|---------|------|
| `ppe_request.cmd reconcile` | Sync + write `CONTROL_PLANE_STATUS.json` |
| `ppe_request.cmd --chapter-id X --reason "..."` | Dry-run route |
| `ppe_request.cmd ... --apply` | Queue to backlog when appropriate |
| `ppe_autobuilder.cmd reconcile` | Same reconcile (pipeline SRE entry) |
| `ppe_autobuilder.cmd status --write` | Lightweight runtime refresh only |
| `ppe_vps_ssh.cmd deploy` | VPS: `git pull` + `docker compose up -d --build` (needs `ppe_operator_ssh.local.cmd`) |
| `msos_production_demo_witness.cmd` | HTTP witness against production URLs (routes + PPE display API + embed surface) |
| `msos_production_playwright_witness.cmd` | Headless browser witness — screenshots + Confirm thesis click on production |

**Production live hookup charter:** [`MSOS_PRODUCTION_LIVE_HOOKUP_V1.md`](MSOS_PRODUCTION_LIVE_HOOKUP_V1.md) — usable demo gap (relay DONE ≠ production walkable). SSH keys stay in gitignored `ppe_operator_ssh.local.cmd`; never paste keys in chat.

---

## Related

- [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) — machine + button for each verdict
- [`CONTEXT_WINDOW_CLOSEOUT_V1.md`](CONTEXT_WINDOW_CLOSEOUT_V1.md) — thread handoff (not chapter truth)
