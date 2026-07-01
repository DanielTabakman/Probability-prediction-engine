# Agent context rules (SOP pointer)

**Purpose:** agent-facing thread/context discipline without editing repo-root `docs/CONTEXT_RULES.md` (product canon layer).

**Full human canon:** [`../CONTEXT_RULES.md`](../CONTEXT_RULES.md)

**Agent routing (load order, verdict → command):** [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)

**Thread openers:** [`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md) · rules: [`.cursor/rules/ppe-roles.mdc`](../../.cursor/rules/ppe-roles.mdc)

---

## Quick rules

1. New context when the **optimization target** changes — not every tiny action.
2. **Operator thread** → `OPERATOR_STATUS.md` + continuity brief; check **`Mode:`** line.
3. **Charter thread** → one program doc; **no** relay / `OPERATOR_STATUS`.
4. **IDE BUILD thread** → starter file only.
5. After chapter closeout → new thread + `AGENT_CONTINUITY_BRIEF.md` only.

See [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) for the full role table.

---

## Agent communication

**Proactive is good; don't personalize without a source.**

Agents may raise unprompted notes when useful. Ground them in repo evidence (path, command, doc) or mark as hypothesis — not as facts about the operator's other systems unless verified.

**Operator threads — do not ask, do not delegate:**

- The operator is not a router. **Never** end with choice questions (`Want me to…?`, `Should I… first?`, `…or …?`).
- **Never** label agent relay commands as operator steps (`DESKTOP_CONTINUE`, `@ppe-director`, queue promotion, branch cleanup).
- **Default:** decide from `OPERATOR_STATUS` + VM SSOT, execute (burst / workers), report what happened. Operator action is usually **nothing** or **`what's next?`** later.
- Full reply format: [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) § Operator-facing replies · rule: [`.cursor/rules/ppe-operator.mdc`](../../.cursor/rules/ppe-operator.mdc).
