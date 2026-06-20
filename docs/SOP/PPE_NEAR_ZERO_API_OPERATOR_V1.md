# PPE near-zero API operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run relay chapters and product BUILD with **minimal headless agent CLI / ACP** usage — or use the **hybrid local default** when auto-build is enabled.

**Related:** [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json)

---

## Two modes

| Mode | Config | On `IDE_BUILD` |
|------|--------|----------------|
| **Hybrid local (default)** | `autoRemoteBuild: true`, `buildWorker: codex`, `preferIdeOverCli: false` in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) | Loop/watch tries **Codex CLI** headless first; desktop Codex handoff or Cursor when blocked |
| **Strict near-zero** | `ppe_operator_near_zero_api.local.cmd` (gitignored) | **IDE handoff only** — no loop CLI |

---

## Three lanes

| Lane | Entry | API credits? |
|------|--------|----------------|
| **Local loop** | `run_ppe_auto_local_loop.cmd` | **No** — control/smoke/closeout |
| **IDE product** | Cursor Agent + `IDE_BUILD_STARTER` | **IDE plan** (not ACP relay) |
| **Headless CLI** | `autoRemoteBuild` when hybrid default | **Yes** — agent CLI on desktop; falls back to IDE handoff on quota |

---

## Quick setup

### Hybrid default (current local profile)

1. [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) sets `autoRemoteBuild: true` and `preferIdeOverCli: false`.
2. One-time desktop: `setup_cursor_agent.cmd` → `agent login` → `verify_cursor_agent.cmd`.
3. Restart stack on loop host: `run_ppe_headless_stack.cmd` or ntfy `restart`.

### Strict IDE-only (optional override)

1. Copy [`ppe_operator_near_zero_api.local.cmd.example`](../../ppe_operator_near_zero_api.local.cmd.example) → `ppe_operator_near_zero_api.local.cmd` (gitignored).
2. Sets `PPE_AUTO_REMOTE_BUILD=0`, `PPE_FORCE_IDE_HANDOFF=1`, `PPE_PREFER_IDE_OVER_CLI=1`.
3. Restart stack.

---

## What happens on exit 7 (`IDE_BUILD`)

**Hybrid (default):** loop or mobile watch calls `respond_to_ide_build` → headless `agent` / `cursor-sdk` when allowed; ntfy `PPE auto-build started`.

**When CLI blocked (usage / not installed):** same as IDE handoff below.

**IDE handoff path:**

1. Generate `IDE_BUILD_STARTER_<sliceId>.md` for the **next unmarked** product slice.
2. Write `artifacts/orchestrator/IDE_BUILD_NOW.md`.
3. Copy build prompt to **clipboard** (Windows).
4. **Open Cursor** on repo + starter file (when `PPE_IDE_HANDOFF_OPEN=1`).
5. **ntfy:** `PPE IDE BUILD: <sliceId>`.

**Automation (optional):** Cursor Automation on `.cursor/IDE_BUILD_TRIGGER.json` — [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md).

Closeout:

```bat
mark_ide_product_ready.cmd <sliceId> [phasePlan]
run_ppe_local.cmd
```

**Post-build watcher:** if the agent commits but skips closeout, `finish_ide_build.cmd` runs on loop/watch passes.

---

## Env overrides

| Variable | Hybrid default | Strict near-zero |
|----------|----------------|------------------|
| `PPE_AUTO_REMOTE_BUILD` | `1` | `0` |
| `PPE_PREFER_IDE_OVER_CLI` | `0` | `1` |
| `PPE_FORCE_IDE_HANDOFF` | unset | `1` |
| `PPE_IDE_HANDOFF_OPEN` | `0` (config) | `1` |
| `PPE_FORCE_CLI_BUILD` | unset | unset — set `1` for one emergency CLI build |

Manual handoff: `open_ide_handoff.cmd`

---

## Do not (API burn)

- `run_ppe_auto_acp_loop.cmd` without budget
- `stewardCharter: true` on local profile
- Disabling `skipAcp` to “unblock” product slices
- `autoRemoteBuild: true` **and** `stewardCharter` / full ACP loop at the same time

---

## Cursor Automations (optional)

Full setup: [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md). Prompt: [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md).

---

## Emergency CLI (away from desk)

In `ppe_operator_near_zero_api.local.cmd` or one-shot env:

```bat
set "PPE_FORCE_CLI_BUILD=1"
set "PPE_FORCE_IDE_HANDOFF=0"
set "PPE_AUTO_REMOTE_BUILD=1"
```

Send `build` on ntfy once, then restore preferred env and `restart`.
