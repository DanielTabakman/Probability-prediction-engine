# IDE-native operator checklist

Runnable steps for **no API credits** operation. Full runbook: [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md).

---

## Bootstrap

- [ ] Repo includes phase 1+2 operator files (`run_ppe_auto_local_loop.cmd`, `mark_ide_product_ready.cmd`).
- [ ] On `main` (or merge PR with operator changes) before treating this as canonical.
- [ ] `docs/SOP/PPE_AUTO_OPERATOR.json` shows `stewardCharter: false`, `skipAcp: true`.
- [ ] **Desktop first-time:** Cursor Agent on desktop → [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) (loop host + ntfy + Tailscale).

---

## Daily run

- [ ] On **`main`** (or sync before loop): `git checkout main && git pull`.
- [ ] **Preflight:** `python scripts/ppe_operator_status.py` — read `artifacts/orchestrator/OPERATOR_STATUS.md` before starting the loop.
- [ ] **Desktop (always-on):** `start_ppe_desktop_operator.cmd` — loop + mobile watch ([`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)).
- [ ] Or manually: `run_ppe_auto_local_loop.cmd` from repo root (health gate + preflight write `OPERATOR_STATUS.md`) + optional `watch_operator_mobile.cmd`.
- [ ] Optional second terminal: `.\scripts\watch_ppe_live.ps1`.
- [ ] Queue fed: `queued` rows in [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) (local profile does **not** steward-charter when idle).

---

## When the loop stops (product)

- [ ] Read `artifacts/orchestrator/OPERATOR_GUARD_REPORT.md` or `LAST_RUN_REPORT.md`.
- [ ] `generate_ide_build_starter.cmd <sliceId> <phasePlanPath>`
- [ ] **New** Cursor Agent thread — `@` `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md` only.
- [ ] Implement product slice; **commit** on plan `buildBranch`.
- [ ] `mark_ide_product_ready.cmd <sliceId> [phasePlanPath]`
- [ ] `run_ppe_local.cmd`
- [ ] Optional: `workflow_metrics.cmd slice close --slice-id <sliceId> --size M --roundtrips N`
- [ ] Loop continues on next pass (or restart loop).

---

## When credits return

- [ ] Stop **local** loop (Ctrl+C).
- [ ] Use **`run_ppe_auto_acp_loop.cmd`** only — do not run local and ACP loops together.
- [ ] `set CURSOR_API_KEY=...` if steward charter is needed.

---

## After chapter closeout

- [ ] New Cursor thread; load only [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md).
- [ ] Do not paste orchestrator logs into steward chat.

---

## Tips

- **Evidence-only chapters** (no Product slice in plan): loop can run control/smoke/closeout unattended.
- **Mixed chapters** with Product: use marker + `run_ppe_local` after IDE BUILD.
- **Split plans** (control/smoke in one plan, product in another) if you want more unattended control work before IDE BUILD.
- **Multitask:** parallel IDE agents are fine for BUILD; they do not replace `run_ppe_local` or the marker.

---

## Chapter hygiene (avoid false PRODUCT_BLOCKED)

- [ ] When product + smoke are witness-complete on `main`, set evidence doc line 2–4 to **`**Status:** **COMPLETE** YYYY-MM-DD`** (required for skip guards).
- [ ] Do **not** leave witness-complete chapters in backlog **`blocked`** — mark **`done`** or run closeout slice promptly.
- [ ] Loop startup runs `run_codebase_health_gate.py --skip-relay`; manual check: same command from repo root.

---

## Related

- [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md)
- [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)
