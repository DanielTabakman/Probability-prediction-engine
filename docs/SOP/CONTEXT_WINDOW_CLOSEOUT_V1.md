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
Run CONTEXT WINDOW CLOSEOUT per @docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md

1. context_window_closeout.cmd --record --whats-next "<one line>"
2. sync_product_direction.cmd (if direction JSON changed this thread)
3. Complete narrative/triage in draft if needed.
4. Operational sweep: commit+gate ship-now items; push branches.
5. End with AGENT CONTINUITY block.
```

**New chat:** ask `what's next?` — no `@` files required (see **Tracking v2** below).

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
context_window_closeout.cmd --record --thread-role steward --whats-next "Continue msos_user_state_v1: run_ppe_local.cmd"
```

`--record` implies `--render`. Omit `--whats-next` to infer from operator verdict.

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

### 2 — Operational sweep (push / pull / threads)

Work through in order; check each box in the draft report.

| Check | Command / action |
|-------|------------------|
| **Pull** | `git fetch` + `git pull --ff-only` on `main` (desktop) or rely on loop `gitSync` (VM) |
| **Uncommitted work** | Commit with gate (`python scripts/run_pushable_gate.py`) or explicit **PARK** note |
| **Unpushed commits** | `git push -u origin HEAD` on feature branches |
| **Open PRs** | `gh pr list --author @me` — merge-ready vs draft vs abandoned |
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

| Bucket | Meaning | Destination |
|--------|---------|-------------|
| **ship_now** | ≤15 min, gates pass, in declared plane | Commit + push in this closeout pass |
| **operator_next** | Loop / relay / IDE BUILD command | `OPERATOR_STATUS` / `run_ppe_local.cmd` / starter file |
| **build_backlog** | Chartered product/evidence work, not urgent today | [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) (`blocked` default) — see [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md) |
| **human_backlog** | Policy, architecture, tradeoff needs you | [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) — see [`HUMAN_STEWARD_BACKLOG.md`](HUMAN_STEWARD_BACKLOG.md) |
| **park** | Dirty or ambiguous repo state | Named branch/stash + one-line in `HANDOFF.md` only if steward-visible |
| **drop** | Explicitly ruled out | One-line reason (no backlog row) |

**CLI helpers** (optional):

```bat
python scripts/ppe_context_window_closeout.py add-build --chapter-id my_id --reason "[P2] …" --priority medium
python scripts/ppe_context_window_closeout.py add-human --title "…" --summary "…" --priority medium --category governance
```

After `add-human`, run `python scripts/ppe_human_backlog.py render-md`.

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

| Closing thread role | New thread |
|---------------------|------------|
| Steward / guide | Ask **`what's next?`** — agent **auto-executes** operator verdict, then reads `WHATS_NEXT.md` + `AGENT_CONTINUITY_BRIEF.md` |
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
| 2026-06-18 | v2 — `context_windows.jsonl` tracking, `WHATS_NEXT` promotion, radar churn signal |
