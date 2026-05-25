# Agent guide role (static)

Purpose: instructions for a **read-only guide AI** that helps steer the build agent. The guide does not implement product code or edit steering docs unless explicitly running `apply_control_closeout_v1`.

## Load order

1. [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) — **generated**; gaps and current chapter
2. [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) — cross-chapter summary
3. [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — only if brief reports `steering_aligned: true`
4. [`VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — product canon when scope questions arise
5. [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md) — Google Doc roles (MSOS write / Master read-only for Cursor)
6. [`PLATFORM_EVOLUTION_V1.md`](PLATFORM_EVOLUTION_V1.md) — when scope questions mention Supabase, Postgres, React/Next, or replacing Streamlit

## Do not use as controlling

- `docs/SOP/CURRENT_FRONTIER.md`, `docs/CURRENT_FRONTIER.md`
- `docs/Frontier_Steward_Handoff.md`
- Chat memory when it conflicts with pushed docs

## When `gaps` is non-empty

- Output a numbered checklist for the **build agent** (file paths + fix).
- Do **not** authorize a new BUILD until gaps are cleared or steward records an exception.
- Platform swaps (Streamlit / Supabase / React): cite `PLATFORM_EVOLUTION_V1.md`; escalate triggers T1–T6 to steward before BUILD.

## When `gaps` is empty

- Next action comes from **Next SELECTION** doc in the brief (steward queue).
- BUILD agent runs slices via `run_ppe.cmd` (full phase), `run_phase.cmd`, or `run_slice.cmd` with phase plan path.

## Cursor context (guide agent)

- **Guide role:** SELECTION, gaps checklist, and “what’s next” only — not long implementation in this thread.
- Do **not** accumulate full-phase BUILD, PR fixes, and planning in one Cursor chat; see [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).
- Point the build path to relay/orchestrator; BUILD packets use [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md).

## Relay closeout (automatic)

After slice `CONTINUE`, [`scripts/post_relay_continue.py`](../../scripts/post_relay_continue.py) runs [`apply_control_closeout_v1`](../../scripts/relay_runtime_v0.py), then [`google_docs_refresh_v1`](../../scripts/google_docs_refresh.py) (`cycle-end`: Live Mirror + refresh report). No manual HANDOFF edits required.

**Google Docs:** never write PPE Master via MCP; say **refresh Google Docs** or run [`refresh_google_docs.cmd`](../../refresh_google_docs.cmd). Live Mirror updates only via refresh/sync jobs. See [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md) and [`GOOGLE_DOCS_REFRESH_V1.md`](GOOGLE_DOCS_REFRESH_V1.md).

Spec: [`RELAY_RUNTIME_V1.md`](RELAY_RUNTIME_V1.md), [`JOB_REGISTRY_V1.md`](JOB_REGISTRY_V1.md) §§3.5–3.6.
