# Cursor IDE BUILD automation v1

**Plane:** CONTROL-PLANE. **Purpose:** start IDE Agent on product slices when handoff fires — **IDE subscription**, not headless CLI.

**Related:** [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## What this automates

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

## Verify

1. `run_ppe_operator.cmd --brief` → `IDE_BUILD` when a product slice is pending.
2. `open_ide_handoff.cmd` or loop handoff → `.cursor/IDE_BUILD_TRIGGER.json` has `"status": "pending"`.
3. Automation starts Agent within ~1 minute.
4. After closeout: trigger returns to `"status": "idle"`; relay continues via `run_ppe_local`.

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
