# Cursor IDE BUILD automation v1

**Plane:** CONTROL-PLANE. **Purpose:** start IDE Agent on product slices when `IDE_BUILD_NOW.md` updates — **IDE subscription**, not headless CLI.

**Related:** [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## What this automates

When the loop hits `IDE_BUILD`, [`ppe_ide_handoff.py`](../../scripts/ppe_ide_handoff.py) writes:

- `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md`
- `artifacts/orchestrator/IDE_BUILD_NOW.md`

Without automation you open Agent manually. With automation, Cursor starts Agent using the handoff prompt.

**Post-build:** [`ppe_post_build_watcher.py`](../../scripts/ppe_post_build_watcher.py) detects commits on the build branch and runs `mark_ide_product_ready` + `run_ppe_local` if the agent stopped after commit.

---

## Setup (Cursor Automations)

1. Open **Cursor → Automations**.
2. **Create automation** — name: `PPE IDE BUILD on handoff`.
3. **Trigger:** File change on `artifacts/orchestrator/IDE_BUILD_NOW.md`.
4. **Action:** Run Agent with prompt from [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md).
5. **Workspace:** This repo root.
6. **Permissions:** Allow terminal (`run_pushable_gate`, `git`, `mark_ide_product_ready.cmd`, `run_ppe_local.cmd`).

### Prompt (if not loading file)

```text
Read artifacts/orchestrator/IDE_BUILD_NOW.md.
Load ONLY the starter file named in that doc.
Implement the product slice per the starter "## When done (required)" section.
Execute autonomously; do not ask for confirmation.
```

---

## Verify

1. `run_ppe_operator.cmd --brief` → `IDE_BUILD` when a product slice is pending.
2. Confirm `artifacts/orchestrator/IDE_BUILD_NOW.md` after handoff.
3. Automation should start Agent within ~1 minute.
4. After commit: agent closeout **or** `finish_ide_build.cmd` on next loop/watch pass.

---

## Disable

| Goal | Setting |
|------|---------|
| No automation | Delete/disable the Cursor Automation |
| No post-commit finish | `set PPE_POST_BUILD_WATCHER=0` or `ideHandoff.postBuildWatcher: false` |
| No handoff | `set PPE_IDE_HANDOFF=0` |

---

## Related

- [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md)
- [`finish_ide_build.cmd`](../../finish_ide_build.cmd)
