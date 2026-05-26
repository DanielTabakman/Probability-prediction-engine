# PPE Agent and network troubleshooting

When `run_ppe.cmd` or relay slices fail with **`[unavailable]`**, **`timeout waiting for relay_result.json`**, or exit code **20**, start here.

## Quick health gate (run before `run_ppe.cmd`)

From repo root:

```powershell
python scripts/ppe_agent_healthcheck.py --repo-root .
```

Or rely on the automatic gate inside `run_ppe.cmd` (same check).

Pass criteria:

```powershell
& "$env:LOCALAPPDATA\cursor-agent\agent.ps1" status
# must show logged in

& "$env:LOCALAPPDATA\cursor-agent\agent.ps1" --trust -p "Reply with exactly: OK"
# must print OK (not Error: [unavailable])
```

Emergency bypass (not recommended): `set PPE_SKIP_AGENT_CHECK=1` then `run_ppe.cmd`.

## Common causes

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| `Error: [unavailable]` | Cursor Agent API unreachable (gRPC UNAVAILABLE) | Change network (home Wi‑Fi, VPN off); reinstall/update Cursor Agent |
| `curl: (35) CRYPT_E_REVOCATION_OFFLINE` | TLS certificate revocation check blocked (captive/library Wi‑Fi) | Use unrestricted internet; see [AGENT_GIT_SETUP.md](AGENT_GIT_SETUP.md) §5 |
| `No model found` | Broken `~/.cursor/cli-config.json` model selection | Re-pick default model in Cursor or fix `cli-config.json` |
| 30+ minute wait then timeout | Old orchestrator waited full `hardMinutes` after silent ACP failure | Update `ppe-orchestrator-acp`; current stack fails fast + toasts |
| `ACTIVE_RUN` + dead PID | Crashed wrapper left a stale lock | Delete `artifacts/orchestrator/ACTIVE_RUN.json`; set manifest `READY` |

## Notifications

| Variable | Effect |
|----------|--------|
| `PPE_NOTIFY=0` | Disable Windows toasts/beeps (`notify_run_finished`, `notify_run_error`, stall toasts) |
| `PPE_WATCH=0` | Disable stall watchdog (`watch_active_run.py`) |
| `PPE_SKIP_AGENT_CHECK=1` | Skip Agent health gate at `run_ppe` start |

Early failure toasts: `scripts/notify_run_error.ps1` (orchestrator + watchdog backup via `artifacts/orchestrator/run_alert.json`).

Stall toasts: ~15m SUS, ~30m hard kill — see [RELAY_ORCHESTRATOR_RUNBOOK_V1.md](RELAY_ORCHESTRATOR_RUNBOOK_V1.md).

## Recovery after a failed phase run

1. Confirm nothing is running (`run_ppe.cmd --status`).
2. Remove stale `artifacts/orchestrator/ACTIVE_RUN.json` if present.
3. Set `docs/SOP/ACTIVE_PHASE_MANIFEST.json` → `"status": "READY"`.
4. Reset relay in the slice worktree (example slice 001):

```powershell
python scripts/relay_runtime_v0.py --repo-root "_worktrees\acp_orchestrator\MVP1-DisagreementStrip-Control-Slice001-disagreement_strip" abort
python scripts/relay_runtime_v0.py --repo-root "_worktrees\acp_orchestrator\MVP1-DisagreementStrip-Control-Slice001-disagreement_strip" reset
```

5. Fix Agent health gate, then `run_ppe.cmd` from repo root.

## Orchestrator self-test

From `ppe-orchestrator-acp` sibling repo:

```powershell
cd ..\ppe-orchestrator-acp
npm run dev -- selftest-acp
```

Expect a hello sentence, not `[unavailable]`.

## Cannot `git push` from this network

Use **local git-only** mode so slices still commit and promote locally:

```powershell
$env:PPE_LOCAL_GIT_ONLY = "1"
.\run_ppe.cmd
```

See [AGENT_GIT_SETUP.md](AGENT_GIT_SETUP.md) §6. Push later from home:

```powershell
python scripts/ppe_git_network.py --repo-root .
```

## Related

- [RELAY_ORCHESTRATOR_RUNBOOK_V1.md](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
- [AGENT_GIT_SETUP.md](AGENT_GIT_SETUP.md)
