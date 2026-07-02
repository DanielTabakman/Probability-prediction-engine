# Founder vs operator surface v1

**Plane:** CONTROL-PLANE · **Purpose:** one page — what deserves **founder** attention vs what **agents** must execute without surfacing as human todos.

**Vocabulary:** **Founder** = product owner working *on* the product (direction, judgment, external world). **Agent/factory** = relay, BUILD, git, recovery, steering sync — working *in* the product. Legacy docs say "operator" for both; prefer **founder** vs **agent surface** in human-facing replies.

**Related:** [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) · [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) · [`DELEGATION_ENVELOPE_V1.md`](DELEGATION_ENVELOPE_V1.md) · [`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md) · [`.cursor/rules/ppe-operator-core.mdc`](../../.cursor/rules/ppe-operator-core.mdc)

**Collaboration SSOT:** Pulse layers, stall policy, and decision defaults live in [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md). This doc defines founder vs agent *surface*; the charter defines *cadence, honesty, and bookkeeping translation*.

**No permanent collaboration thread:** pulses (L1–L4) + charter doc carry the relationship. Open a fresh `founder_charter` thread only for monthly review or charter edits — see charter § Ongoing integration.

---

## Founder surface — only these deserve attention

| Category | Examples | Agent behavior |
|----------|----------|----------------|
| **Direction** | Plain-language pivot ("drop X, prioritize Y") | Agent edits JSON, syncs, queues, commits — founder does not run sync steps |
| **SELECTION / charter** | Build order, defer vs ship, scope fights | Present **decision packet** (options + recommendation); do not assign factory steps |
| **Policy / architecture** | `HUMAN_STEWARD_BACKLOG` items | Surface only in **founder charter** threads the user opened — never append to operator replies |
| **External world** | Stripe account, VPS keys, Cloudflare, billing | Label **External action:** with one sentence; cannot automate |
| **Live validation** | Tester sessions, trader workflow research | Founder runs sessions; agents log evidence docs after |
| **Canon conflicts** | PPE_MASTER vs repo truth | Report mismatch; ask founder to pick update path — do not resolve silently |

---

## Agent surface — never assign to founder

Agents **execute in-thread** or spawn workers (`@ppe-director`, `@ppe-build-worker`, `@ppe-finish-worker`). Do not list these as founder todos:

- Relay verdicts, burst plan, `what's next?` execution
- `DESKTOP_BUILD` / `DESKTOP_CONTINUE`, mark ready, closeout
- Git: stash, checkout, branch recovery, gate → commit → push → PR
- Steering sync (`sync_product_direction.cmd`), queue promotion, evidence closeout docs
- "Open IDE BUILD thread", `ppe_go.cmd`, mixed-plane recovery
- Weekly verdict checks, backlog hygiene, radar/digest prep
- Context window closeout auto-ship

**Exception (founder manual surface):** double-click **`DESKTOP BUILD`** / **`DESKTOP CONTINUE`** when phone ntfy says `IDE_BUILD` and they are **not** in an agent thread. Otherwise **`what's next?`** in operator thread.

---

## Agent reply contract

Use **one primary closing** per [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) § Agent reply contract. Layer 3 (**Alert:**) overrides all others.

| Closing | Layer | When |
|---------|-------|------|
| **Nothing required from you.** | — | Factory advancing; no founder gap |
| **Completion:** _sentence_ · Next: _line_ · **Nothing required from you.** | L2 | Slice/closeout/chapter step just finished |
| **Alert:** _plain problem_ · _consequence_ · **Decision needed:** or **External action:** | L3 | Stall, deadlock, or founder-only gap — **never** hide behind "nothing required" |
| **Decision needed:** _outcome options + default recommendation_ | L3 | Strategic judgment only — not technical forks |

**Technical decisions:** agents default and execute ([`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) § Decision defaults). Do not ask the founder to choose scripts, branches, or repair paths.

**Forbidden:**

- Numbered factory steps (`git pull`, `DESKTOP_CONTINUE`, open thread, mark ready)
- Choice questions (`Want me to…?`, `Should I… first?`) for **technical** choices
- **Nothing required from you.** when Layer 3 alert conditions are true
- Commit permission prompts
- Pasting `OPERATING_CALENDAR` or `HUMAN_STEWARD_BACKLOG` as end-of-reply todo lists
- Implementation checklists disguised as "next steps for you"

**Good:**

> **Verdict:** `IDE_BUILD` · slice002. Build worker spawned; gate+commit when done. **Nothing required from you.**

**Bad:**

> On this desktop: 1) git pull 2) Open IDE BUILD thread 3) mark ready. Want me to start BUILD or finish status followups first?

---

## Thread routing

| Intent | Opener | Load |
|--------|--------|------|
| Factory / relay | `what's next?` · `THREAD_ROLE: operator` | `OPERATOR_STATUS.md` → burst → workers |
| **Collaboration / how we work** | **Founder collaboration** starter in [`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md) | [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) — **no** relay |
| Product / strategy / SELECTION | **Founder charter** starter in [`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md) | This doc + program doc — **no** `OPERATOR_STATUS` |
| One product slice | `THREAD_ROLE: ide_build` + starter | Starter only |

When founder charter work needs execution → agent parks to operator thread or spawns workers — **does not** ask founder to run relay.

---

## Cadence tags ([`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md))

| Tag | Meaning |
|-----|---------|
| `founder` | Judgment or external world — founder only |
| `agent` | Operator/charter thread runs and reports |
| `digest-only` | Monday ntfy summary; no action unless founder opts in |

Agents must not convert `agent` or `digest-only` rows into founder todo lists in unrelated threads.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | v1 — founder vs agent surface SSOT; reply contract; cadence tags |
| 2026-07-02 | Link FOUNDER_COLLABORATION_CHARTER_V1; layered closings; L3 alert overrides |
