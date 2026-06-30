# Thread starters v1

**Plane:** CONTROL-PLANE · **Purpose:** copy-paste openers so relay/autobuilder does not hijack topic threads.

**Rules:** [`.cursor/rules/ppe-thread-roles.mdc`](../../.cursor/rules/ppe-thread-roles.mdc) · [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) · [`CONTEXT_RULES.md`](../CONTEXT_RULES.md)

---

## Operator / autobuilder (relay + what's next)

Dedicated thread for queue, VM status, burst, and triage. Open **one** long-lived operator chat or a fresh thread when you want relay work.

```text
Operator thread. THREAD_ROLE: operator.
Run what's next per ppe-operator-core (burst + @ppe-director when allowed).
Do not mix UX charter or SELECTION planning here.
```

Minimal:

```text
what's next?
```

After context closeout:

```text
what's next?
```

Optional @ files: `artifacts/orchestrator/OPERATOR_STATUS.md`, `docs/SOP/AGENT_CONTINUITY_BRIEF.md`

---

## IDE BUILD (one slice)

```text
IDE BUILD thread. THREAD_ROLE: ide_build.
Load only @artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md
Implement → gate → mark_ide_product_ready. No steward narrative.
```

---

## Charter / topic (UX, data, SELECTION, programs)

Use for planning, backlog edits, and domain work **without** relay bleed.

```text
Charter thread. THREAD_ROLE: charter.
Do NOT read OPERATOR_STATUS or run relay/burst.
Topic: [e.g. trader learning spine UX / distribution data collection]
Load only: @docs/SOP/UX_EXECUTION_BACKLOG_V1.md
Park any relay/IDE_BUILD work for the operator thread.
```

UX design only (no execution):

```text
Charter thread — UX design only.
Load @docs/SOP/MSOS_UX_DESIGN_PHILOSOPHY_V1.md and @docs/SOP/UX_EXECUTION_BACKLOG_V1.md.
@ppe-ux-charter — no OPERATOR_STATUS.
```

Data / asset program:

```text
Charter thread. THREAD_ROLE: charter.
Topic: asset batch / data collection
Load only: @docs/SOP/ASSET_BATCH_EXPANSION_POLICY_V1.md (or relevant program doc).
```

Unclear topic — resolve first:

```text
Charter thread. THREAD_ROLE: charter.
Run: python scripts/resolve_sop.py --topic "<your topic>" --json
Load only paths from load_always in the JSON.
```

---

## Topic quick reference

| Topic | @ file or command |
|-------|-------------------|
| UX backlog | `docs/SOP/UX_EXECUTION_BACKLOG_V1.md` |
| Trader spine | `docs/SOP/TRADER_LEARNING_SPINE_PROGRAM_V1.md` |
| Asset enable | `python scripts/discover_asset_data_source.py --asset ID --json` |
| Asset batch | `docs/SOP/ASSET_BATCH_EXPANSION_POLICY_V1.md` |
| Any chapter | `python scripts/resolve_sop.py --chapter <id> --json` |

Full table: [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) § Topic → load.

---

## Explore / review

```text
Explore thread. THREAD_ROLE: explore.
Review only — no relay, no commits unless I ask.
```

---

## VM + desktop layout (operator thread only)

Do **not** use this in charter threads — it pulls operator status by default.

```text
Operator thread. THREAD_ROLE: operator.
Load @docs/SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md
VM loop host: ppeloop@DESKTOP-CAQLL8K. Desktop is IDE BUILD only.
Run what's next; do not restart VM loop unless STACK_DOWN.
```

---

## Switching roles mid-thread

| Phrase | Effect |
|--------|--------|
| `switch to operator` / `what's next?` | Operator role for this turn onward |
| `stay in charter` / `charter only` | Re-lock charter; stop citing relay |
| `close out thread` | Context closeout per [`CONTEXT_WINDOW_CLOSEOUT_V1.md`](CONTEXT_WINDOW_CLOSEOUT_V1.md) |

---

## Anti-patterns

| Avoid | Use instead |
|-------|-------------|
| Opening UX chat with no role → agent reads `IDE_BUILD` | `Charter thread` + program doc |
| `@ppe-ux-director` for UX brainstorming | Charter thread + `@ppe-ux-charter` |
| Steward + operator + BUILD in one thread | Separate operator vs charter vs IDE BUILD |
| Pasting `OPERATOR_STATUS` into charter threads | One-line "see operator thread" if needed |
