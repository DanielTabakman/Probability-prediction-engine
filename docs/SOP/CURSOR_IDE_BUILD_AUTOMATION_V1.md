# Cursor IDE BUILD automation v1

**Plane:** CONTROL-PLANE. **Purpose:** auto-start IDE BUILD on product slices when handoff fires.

**Related:** [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## Recommended: local trigger watcher (desktop)

**Default on the always-on desktop.** No Cursor cloud Automations required.

When handoff fires, [`ppe_ide_handoff.py`](../../scripts/ppe_ide_handoff.py) writes **`.cursor/IDE_BUILD_TRIGGER.json`** with `"status": "pending"`.  
[`watch_ide_build_local.cmd`](../../watch_ide_build_local.cmd) polls that file and starts the **local agent CLI** against your repo.

```text
Loop exit 7 → handoff writes trigger (pending)
            → watch_ide_build_local.cmd sees change (~5s)
            → agent CLI implements starter + closeout
            → post-build watcher or mark_ide_product_ready → run_ppe_local
```

| Item | Value |
|------|-------|
| **Watcher** | `watch_ide_build_local.cmd` (started by `start_ppe_desktop_operator.cmd`) |
| **Config** | `ideHandoff.localTriggerWatcher: true` in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) |
| **Prerequisite** | `setup_cursor_agent.cmd` + `agent login` on the desktop |
| **Disable** | `PPE_IDE_LOCAL_TRIGGER_WATCHER=0` or `localTriggerWatcher: false` |

**Post-build:** [`ppe_post_build_watcher.py`](../../scripts/ppe_post_build_watcher.py) runs `mark_ide_product_ready` + `run_ppe_local` if the agent stops after commit.

---

## Legacy: Cursor cloud Automations (optional)

Cloud Automations (webhook / GitHub-connected) hit **background composer quota** and do not watch the local workspace reliably. Prefer the **local watcher** above.

### What handoff still writes

When the loop hits `IDE_BUILD`, [`ppe_ide_handoff.py`](../../scripts/ppe_ide_handoff.py) writes:

- `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md` — BUILD packet
- `artifacts/orchestrator/IDE_BUILD_NOW.md` — human instructions (not a valid Automation trigger)
- **`.cursor/IDE_BUILD_TRIGGER.json`** — **Automation trigger** (`status: pending`, `starter`, `sliceId`, …)
- `artifacts/orchestrator/IDE_HANDOFF_STATE.json` — machine state (alternate trigger if UI allows `artifacts/` JSON)

Without automation you open Agent manually. With automation, Cursor starts Agent using the trigger JSON.

**Post-build:** [`ppe_post_build_watcher.py`](../../scripts/ppe_post_build_watcher.py) detects commits on the build branch and runs `mark_ide_product_ready` + `run_ppe_local` if the agent stopped after commit. `mark_ide_product_ready` sets the trigger back to `idle`.

---

## Setup (Cursor Automations)

**Quick start:** `setup_cursor_ide_build_automation.cmd` — opens Automations and writes `artifacts/orchestrator/CURSOR_IDE_BUILD_AUTOMATION_SETUP.md`.

### Primary trigger (recommended)

Cursor Automations **do not support `.md` file triggers**. Use JSON:

1. Open **Cursor → Automations → Create automation** — name: `PPE IDE BUILD on handoff`.
2. **Trigger:** File change on **`.cursor/IDE_BUILD_TRIGGER.json`** (repo root workspace).
3. **Action:** Run Agent with prompt from [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md).
4. **Workspace:** This repo root (local IDE workspace — `artifacts/` is gitignored).
5. **Permissions:** Allow terminal (`run_pushable_gate`, `git`, `mark_ide_product_ready.cmd`, `run_ppe_local.cmd`).

### Alternate triggers (if JSON file watch unavailable)

| Trigger | Notes |
|---------|--------|
| **File change** on `artifacts/orchestrator/IDE_HANDOFF_STATE.json` | Same handoff moment; prompt: read `last_starter` + `last_handoff_slice` |
| **Webhook** | Set `PPE_CURSOR_AUTOMATION_WEBHOOK_URL` (+ optional `PPE_CURSOR_AUTOMATION_WEBHOOK_KEY`); handoff POSTs payload after writing trigger |
| **Schedule (2–5 min)** | Poll `.cursor/IDE_BUILD_TRIGGER.json`; no-op unless `status` is `pending` |
| **ntfy + `@ppe-director`** | No Automation; manual/phone fallback |

### Prompt (if not loading file)

```text
Read .cursor/IDE_BUILD_TRIGGER.json.
If status is not "pending", exit with no-op.
Load ONLY the starter path from the trigger file.
Implement per starter "## When done (required)" (gate, commit, mark_ide_product_ready, run_ppe_local).
Execute autonomously; do not ask for confirmation.
```

---

## Health check (which part is broken)

```bat
check_ide_build_automation.cmd
```

Writes `artifacts/orchestrator/IDE_BUILD_AUTOMATION_HEALTH.md` with per-check codes.

| Exit | Verdict | Meaning |
|------|---------|---------|
| 0 | `OK` | Wiring good; cloud BUILD should fire on handoff |
| 2 | `QUOTA_BLOCKED` | Wiring good; Cursor quota exhausted — retry after billing cycle |
| 1 | `BROKEN` | Fix blocker code in report (URL, key, handoff disabled, etc.) |

Handoff webhook failures also write `artifacts/orchestrator/IDE_BUILD_AUTOMATION_LAST_ERROR.json` with `code` + `fix_hint`. Paste that code into a steward thread if stuck.

**Will it work?** Yes, once quota returns: cloud agent implements + commits; local post-build watcher (or `finish_ide_build.cmd`) runs `mark_ide_product_ready` + `run_ppe_local`. Manual fallback: `@` starter in a new Agent thread.

---

## Verify

1. `check_ide_build_automation.cmd` → `OK` or `QUOTA_BLOCKED` (not `BROKEN`).
2. `run_ppe_operator.cmd --brief` → `IDE_BUILD` when a product slice is pending.
3. `open_ide_handoff.cmd` or loop handoff → `.cursor/IDE_BUILD_TRIGGER.json` has `"status": "pending"`.
4. Automation run appears in Cursor Automations history (when quota allows).
5. After closeout: trigger returns to `"status": "idle"`; relay continues via `run_ppe_local`.

---

## Disable

| Goal | Setting |
|------|---------|
| No automation | Delete/disable the Cursor Automation |
| No webhook | Unset `PPE_CURSOR_AUTOMATION_WEBHOOK_URL` |
| No post-commit finish | `set PPE_POST_BUILD_WATCHER=0` or `ideHandoff.postBuildWatcher: false` |
| No handoff | `set PPE_IDE_HANDOFF=0` |

---

## Related

- [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md)
- [`.cursor/IDE_BUILD_TRIGGER.json`](../../.cursor/IDE_BUILD_TRIGGER.json)
- [`finish_ide_build.cmd`](../../finish_ide_build.cmd)
