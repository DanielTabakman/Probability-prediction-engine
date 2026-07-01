# Context window closeout v1

**Plane:** CONTROL-PLANE · **Layer:** `dev-factory`

**Purpose:** End a long or noisy **Cursor chat** without losing track of what started, what shipped, what still needs a human, and what belongs in build queues. This is **not** chapter closeout (`apply_control_closeout_v1`) — it is the ritual for **retiring a context window** while repo truth stays legible.

**Related:** [`CONTEXT_RULES.md`](../CONTEXT_RULES.md) · [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md) · [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) · relay ritual in [`LAST_RUN_REPORT.md`](../../artifacts/orchestrator/LAST_RUN_REPORT.md) (orchestrator exit only)

---

## When to run

| Signal | Action |
|--------|--------|
| Optimization target changed (bug → feature, BUILD → planning) | Closeout **before** opening the new thread |
| Thread is **WATCH** / **ESCALATE** per [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) | Closeout now; do not add more scope |
| You cannot answer “what is still open in this chat?” in one sentence | Closeout |
| Chapter / slice **relay closeout** completed | Run **this** closeout if the Cursor thread also did ad-hoc work |
| Leaving laptop / handoff to another device | Closeout + git sweep (see [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md)) |

**Do not** run context closeout mid-BUILD when the working tree is dirty **unless** you are parking state on purpose (record **PARK** bucket).

---

## Two closeouts (do not confuse)

| Kind | Trigger | Updates | Next thread loads |
|------|---------|---------|-------------------|
| **Chapter closeout** | Relay slice with `closeout:` → `CONTINUE` | `HANDOFF`, frontier, `AGENT_CONTINUITY_BRIEF`, **direction markers** (automated via `sync_product_direction`) | `AGENT_CONTINUITY_BRIEF.md` + `ACTIVE_PRODUCT_DIRECTION.json` |
| **Context window closeout** | Steward says “close this chat” | Draft report + backlog triage + git/PR sweep | Brief + this report’s **Next thread** section |

Chapter closeout can happen **without** context closeout when the Cursor thread was already short. Context closeout can happen **without** chapter closeout when the thread was exploratory or mixed ad-hoc fixes.

---

---

## Triggers (say any of these)

The Agent should run this ritual when you use **any** of:

| Phrase | Notes |
|--------|--------|
| **close out thread** | Primary operator phrase |
| **closeout thread** | Same intent |
| **close this thread** / **end this thread** | |
| **context closeout** / **close out context** | |
| **wrap this chat** / **thread handoff** | Informal |

Shorthand paste (minimal):

```text
close out thread
```

Full paste (when you want the checklist explicit):

```text
Run CONTEXT WINDOW CLOSEOUT per @docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md
```

---

## Operator one-liner (paste in Agent)

```text
close out thread
```

That runs **auto-ship + record** — no git narration to the operator.

Explicit checklist (optional):

```text
Run CONTEXT WINDOW CLOSEOUT per @docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md

context_window_closeout.cmd --record
```

**New chat:** ask `what's next?` — no `@` files required (see **Tracking v2** below).

---

## Auto-ship (default on `--record`)

`context_window_closeout.cmd --record` runs **`ppe_context_closeout_ship.py`** before writing the draft:

| Step | Behavior |
|------|----------|
| **Clean tree, unpushed commits** | Push + open PR if missing + `automerge` label |
| **Dirty shippable files** | Branch `ops/closeout-*` if on `main` → gate → commit → push → PR |
| **Mixed-plane dirty** | **Park** — no unsafe auto-commit; recovery thread |
| **Charter / explore closeout + mixed-plane** | **Park** in draft — no branch surgery; next thread: operator `what's next?` or same charter topic |
| **Gate failure** | Unstage + park paths in draft report |
| **Merge** | **Never** ask the operator — CI + merge-on-green |

Skip auto-ship (triage-only): `context_window_closeout.cmd --record --no-ship`

Preview only: `context_window_closeout.cmd --ship-dry-run --render`

**Operator rule:** agents report **"thread closed — shipped"** or **"thread closed — parked (recovery)"** — not commit/PR/merge play-by-play.

---

## Tracking v2 (append + what's next)

Each `--record` closeout:

| Artifact | Purpose |
|----------|---------|
| `artifacts/workflow_metrics/context_windows.jsonl` | Append-only history (one row per closeout) |
| `artifacts/control_plane/WHATS_NEXT.md` | Latest one-liner for agents + operators |
| `artifacts/control_plane/WHATS_NEXT.json` | Machine payload for tooling |

`OPERATOR_STATUS.md` includes the **What's next** block when `WHATS_NEXT.md` exists. Weekly radar flags **context-chat-churn** when ≥3 closeouts in a week and zero slices closed.

```bat
context_window_closeout.cmd --record --thread-role charter --whats-next "Continue UX backlog edits per UX_EXECUTION_BACKLOG_V1.md"
context_window_closeout.cmd --record --thread-role operator --whats-next "Continue msos_user_state_v1: run_ppe_local.cmd"
```

`--record` implies `--render`. Omit `--whats-next` to infer from operator verdict. **Charter/steward closeouts:** always pass `--thread-role charter` (legacy `steward` aliases to charter).

---

## Steps (agent checklist)

### 1 — Machine facts (script)

From repo root:

```bat
context_window_closeout.cmd --render
REM or: python scripts/ppe_context_window_closeout.py --render  (from repo root with PYTHONPATH=%CD%)
```

Reads: git preflight, manifest, operator verdict, open PRs (if `gh` available). Writes:

- `artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT.json`
- `artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT_DRAFT.md`

Do **not** hand-author branch/ahead/behind/dirty-file facts when the script ran successfully.

### 2 — Operational sweep (automatic)

**Default:** `context_window_closeout.cmd --record` runs auto-ship (`scripts/ppe_context_closeout_ship.py`).

Manual checklist (only when `--no-ship` or auto-ship blocked):

| Check | Command / action |
|-------|------------------|
| **Pull** | `git fetch` + `git pull --ff-only` on `main` (desktop) or rely on loop `gitSync` (VM) |
| **Uncommitted work** | Auto-ship commits or **PARK** in draft |
| **Unpushed commits** | Auto-ship push + PR |
| **Open PRs** | Auto-ship labels `automerge`; CI merges — no operator click |
| **Operator thread** | `artifacts/orchestrator/OPERATOR_STATUS.md` — verdict matches what you think |
| **Relay thread** | `artifacts/orchestrator/LAST_RUN_REPORT.md` if a phase run happened this session |
| **IDE BUILD starter** | If `IDE_BUILD` pending, note `artifacts/orchestrator/IDE_BUILD_STARTER_*.md` path |
| **Stash / worktrees** | Name any stash or worktree that must survive the thread death |

### 3 — Journey narrative (agent-written)

Fill **Meta — what happened** in the draft:

- **What** — outcomes delivered this window (commits, PRs, docs, decisions)
- **Why** — optimization target at start vs end
- **How it arose** — trigger (ntfy, steward packet, bug, scope creep, operator error)
- **Threads inventory** — table: topic | started | finished | abandoned | owner next

Chat memory is **not** ground truth. Reconcile against git log and pushed docs.

### 4 — Triage buckets

Sort every open item **exactly one** bucket:

| Bucket | Meaning | Lane | Destination |
|--------|---------|------|-------------|
| **ship_now** | ≤15 min, gates pass, in declared plane | control_plane | Commit + push in this closeout pass |
| **operator_next** | Loop / relay / IDE BUILD command | relay | Operator thread — `what's next?` (not charter execution) |
| **build_backlog** | Chartered product/evidence work, not urgent today | control_plane | [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) |
| **triggered_ideas** | Great idea, too early — revisit when a chapter matches | control_plane | [`TRIGGERED_IDEAS.json`](TRIGGERED_IDEAS.json) |
| **human_backlog** | Policy, architecture, tradeoff needs you | human | [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) |
| **park** | Dirty or ambiguous repo state | mixed | Named branch/stash; recovery → operator thread |
| **drop** | Explicitly ruled out | — | One-line reason (no backlog row) |

Classify ambiguous items with `scripts.ppe_thread_roles.classify_parked_lane` — see [`.cursor/rules/ppe-thread-roles.mdc`](../../.cursor/rules/ppe-thread-roles.mdc) § Parked items.

**CLI helpers** (optional):

```bat
python scripts/ppe_context_window_closeout.py add-build --chapter-id my_id --reason "[P2] …" --priority medium
python scripts/ppe_context_window_closeout.py add-human --title "…" --summary "…" --priority medium --category governance
python scripts/ppe_context_window_closeout.py add-triggered --title "…" --summary "…" --trigger-chapter msos_wallet_connect_v1 --trigger-keyword "wallet connect"
```

After `add-human`, run `python scripts/ppe_human_backlog.py render-md`. Triggered ideas auto-render on add/dismiss.

### 5 — AGENT CONTINUITY block (required)

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
  - artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT_DRAFT.md (completed)
  - docs/SOP/AGENT_CONTINUITY_BRIEF.md
  - (optional) specific SELECTION / starter paths
- If NO: what must the next agent finish in-repo first:
```

Report **doc-state safety** and **repo-state safety** separately ([`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md)).

### 6 — Next thread boot

**Thread roles:** [`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md) · [`.cursor/rules/ppe-thread-roles.mdc`](../../.cursor/rules/ppe-thread-roles.mdc)

| Closing thread role | New thread |
|---------------------|------------|
| **Operator** / steward relay | Ask **`what's next?`** in operator thread — burst + director when allowed; `WHATS_NEXT.md` + `AGENT_CONTINUITY_BRIEF.md` |
| **Charter** / topic | Same charter doc or new `Charter thread` opener — **not** operator unless relay blocked |
| IDE BUILD | Starter file only — **not** steward narrative |
| Recovery | `what's next?` or `@docs/SOP/RECOVERY_PROTOCOL.md` if recovery-specific |

Optional `@artifacts/control_plane/WHATS_NEXT.md` if the agent does not self-read.

**Never** paste orchestrator stdout, full pytest logs, or full `git diff` into the next thread.

---

## Window ledger (optional)

If the steward maintained a ledger this window ([`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md)):

`Ledger — Roundtrips: X | Raw copy-pastes: Y | Slices closed: Z | Active slice: ___ | Next step: ___`

Copy final numbers into the draft report **Window ledger** section.

---

## Anti-patterns

- Closing the chat without a draft report when anything remains uncommitted or untriaged
- Stuffing build-sized work into **ship_now** to avoid backlog hygiene
- Using **human_backlog** for normal product slices (use **build_backlog**)
- Treating chat summary as canonical over `AGENT_CONTINUITY_BRIEF` / frontier docs
- One mega-thread across SELECTION + BUILD + closeout + PR triage + context closeout

---

## Changelog

| Date | Note |
|------|------|
| 2026-06-17 | v1 — SOP + `ppe_context_window_closeout.py` gather/triage helpers |
| 2026-06-28 | v3 — `--record` default auto-ship (`ppe_context_closeout_ship.py`); operator silence on git/PR |
| 2026-06-18 | v2 — `context_windows.jsonl` tracking, `WHATS_NEXT` promotion, radar churn signal |
