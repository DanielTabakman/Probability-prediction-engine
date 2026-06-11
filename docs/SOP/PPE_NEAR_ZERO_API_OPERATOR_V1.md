# PPE near-zero API operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run relay chapters and product BUILD with **minimal headless agent CLI / ACP** usage.

**Related:** [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json)

---

## Three lanes (default)

| Lane | Entry | API credits? |
|------|--------|----------------|
| **Local loop** | `run_ppe_auto_local_loop.cmd` | **No** — control/smoke/closeout |
| **IDE product** | Cursor Agent + `IDE_BUILD_STARTER` | **IDE plan** (not headless CLI) |
| **Headless CLI** | phone `build` when explicitly enabled | **Yes** — use sparingly |

---

## Quick setup

1. [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) already sets `autoRemoteBuild: false` and `ideHandoff.preferIdeOverCli: true`.
2. Copy [`ppe_operator_near_zero_api.local.cmd.example`](../../ppe_operator_near_zero_api.local.cmd.example) → `ppe_operator_near_zero_api.local.cmd` (gitignored).
3. Restart stack: `run_ppe_desktop_operator.cmd` or ntfy `restart`.

---

## What happens on exit 7 (`IDE_BUILD`)

1. **No headless CLI** (unless `PPE_FORCE_CLI_BUILD=1`).
2. Generate `IDE_BUILD_STARTER_<sliceId>.md` for the **next unmarked** product slice.
3. Write `artifacts/orchestrator/IDE_BUILD_NOW.md`.
4. Copy build prompt to **clipboard** (Windows).
5. **Open Cursor** on repo + starter file.
6. **ntfy:** `PPE IDE BUILD: <sliceId>`.

**Automation (recommended):** Cursor Automation on `IDE_BUILD_NOW.md` — [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md).

**Manual:** new Agent thread → `@` starter → paste handoff prompt.

Closeout (in starter **## When done** or handoff clipboard):

```bat
mark_ide_product_ready.cmd <sliceId> [phasePlan]
run_ppe_local.cmd
```

**Post-build watcher:** if the agent commits but skips closeout, `finish_ide_build.cmd` runs on loop/watch passes.

---

## Env overrides

| Variable | Default (near-zero) | Effect |
|----------|---------------------|--------|
| `PPE_AUTO_REMOTE_BUILD` | `0` | Loop/watch do not start headless CLI |
| `PPE_FORCE_IDE_HANDOFF` | `1` | phone `build` → IDE handoff |
| `PPE_PREFER_IDE_OVER_CLI` | `1` | Skip CLI even if agent installed |
| `PPE_IDE_HANDOFF_OPEN` | `1` | Open Cursor on handoff |
| `PPE_IDE_HANDOFF_CLIPBOARD` | `1` | Copy prompt to clipboard |
| `PPE_FORCE_CLI_BUILD` | unset | Set `1` for one emergency CLI build |

Manual handoff:

```bat
open_ide_handoff.cmd
```

---

## Do not (API burn)

- `run_ppe_auto_acp_loop.cmd` without budget
- `stewardCharter: true` on local profile
- `autoRemoteBuild: true` while relying on IDE for product
- Disabling `skipAcp` to “unblock” product slices

---

## Cursor Automations (recommended)

Full setup: [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md). Prompt: [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md).

---

## Emergency CLI (away from desk)

In `ppe_operator_near_zero_api.local.cmd`:

```bat
set "PPE_FORCE_CLI_BUILD=1"
set "PPE_FORCE_IDE_HANDOFF=0"
set "PPE_AUTO_REMOTE_BUILD=1"
```

Send `build` on ntfy once, then restore near-zero env and `restart`.
