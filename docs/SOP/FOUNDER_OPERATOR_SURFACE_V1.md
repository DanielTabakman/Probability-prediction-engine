# Founder vs operator surface v1

**Plane:** CONTROL-PLANE · **Purpose:** one page — what deserves **founder** attention vs what **agents and runtime automation** must execute without surfacing as human todos.

**Vocabulary:** **Founder** = product owner working *on* the product (direction, judgment, external world). **Agent/factory** = relay, BUILD, git, recovery, steering sync — working *in* the product. Legacy docs say "operator" for both; prefer **founder** vs **agent surface** in human-facing replies.

**Related:** [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) · [`DELEGATION_ENVELOPE_V1.md`](DELEGATION_ENVELOPE_V1.md) · [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) · [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · [`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md) · [`.cursor/rules/ppe-operator-core.mdc`](../../.cursor/rules/ppe-operator-core.mdc)

---

## Runtime automation is SSOT (default day-to-day)

**Founder never opens Cursor threads, pastes starters, or runs relay commands for factory work.** That is not the normal process.

On a typical day the **headless stack** on the VM loop host ([`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md)) runs factory unattended:

| Layer | Config / entry | What runs without founder |
|-------|----------------|---------------------------|
| Relay loop | `run_ppe_headless_stack.cmd --ensure` | Control / witness / closeout slices |
| IDE BUILD dispatch | `autoRemoteBuild: true` in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) | Codex CLI (or agent CLI) on `IDE_BUILD` |
| Post-build | `ideHandoff.postBuildWatcher: true` | Mark ready + `run_ppe_local` after BUILD |
| Local trigger | `ideHandoff.localTriggerWatcher: true` | Desktop watcher on BUILD triggers |
| Git sync | `gitSync.*EachPass: true` | Pull / publish / merge each loop pass |
| Monday digest | `weekly_digest_monday.cmd` (scheduled) | Radar + backlog titles (digest-only) |

**Canonical factory path:** VM loop → autoRemoteBuild → headless BUILD → postBuildWatcher → relay continues.

**Cursor chat** (`what's next?`, operator thread, `@ppe-director`, IDE BUILD starter) is **agent/degraded-mode** — for when automation fails, agents are debugging, or a charter pass is open. **Not** the founder's daily ritual.

**Founder on a normal factory day:** nothing. Optional: read ntfy digest; no action required.

---

## Degraded mode only (founder optional — not default)

When automation is down or headless BUILD fails, these exist as **overrides** — agents should try them before asking the founder:

| Override | Who uses it |
|----------|-------------|
| ntfy `build` / `fix` | Agent or founder one-tap on phone ([`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)) |
| `ppe_autobuilder.cmd advance` | Agent / `@ppe-autobuilder-operator` |
| Cursor operator thread + burst | Agent-initiated — **not** founder homework |
| `DESKTOP BUILD` / `DESKTOP CONTINUE` double-click | Last-resort when stack cannot dispatch ([`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) § degraded) |

Agents document degraded mode in status; default reply remains **Nothing required from you.**

---

## Founder surface — only these deserve attention

| Category | Examples | Agent behavior |
|----------|----------|----------------|
| **Direction** | Plain-language pivot ("drop X, prioritize Y") | Agent edits JSON, syncs, queues, commits — founder does not run sync steps |
| **SELECTION / charter** | Build order, defer vs ship, scope fights | Present **decision packet** (options + recommendation); do not assign factory steps |
| **Policy / architecture** | `HUMAN_STEWARD_BACKLOG` items | Surface only when founder opens a charter pass — never append to operator replies |
| **External world** | Stripe account, VPS keys, Cloudflare, billing | Label **External action:** with one sentence; cannot automate |
| **Live validation** | Tester sessions, trader workflow research | Founder runs sessions; agents log evidence docs after |
| **Canon conflicts** | PPE_MASTER vs repo truth | Report mismatch; ask founder to pick update path — do not resolve silently |

---

## Agent surface — never assign to founder

Runtime + agents own these end-to-end:

- Headless stack, relay loop, autobuilder `advance`
- `autoRemoteBuild`, postBuildWatcher, localTriggerWatcher
- Relay verdicts, burst, `@ppe-director` / build / finish workers
- `DESKTOP_CONTINUE`, mark ready, closeout (via automation or agent)
- Git: stash, checkout, branch recovery, gate → commit → push → PR
- Steering sync, queue promotion, evidence closeout docs
- Weekly verdict checks, backlog hygiene, radar/digest prep
- Context window closeout auto-ship

Do **not** tell the founder to open threads, paste starters, or run `what's next?` for factory.

---

## Agent reply contract

End founder-facing replies with **one** of:

| Closing | When |
|---------|------|
| **Nothing required from you.** | Factory handled, in progress, or runtime automation owns next step |
| **Decision needed:** _one sentence + options_ | Strategic judgment only |
| **External action:** _one sentence_ | Accounts, credentials, live sessions agents cannot run |

**Forbidden:**

- Numbered factory steps (`git pull`, `DESKTOP_CONTINUE`, open thread, mark ready, `what's next?`)
- Treating Cursor thread openers as founder daily process
- Choice questions (`Want me to…?`, `Should I… first?`)
- Commit permission prompts
- Pasting `OPERATING_CALENDAR` or `HUMAN_STEWARD_BACKLOG` as end-of-reply todo lists

**Good:**

> Headless stack owns closeout; postBuildWatcher will continue relay. **Nothing required from you.**

**Bad:**

> Open an operator thread and ask what's next? Or double-click DESKTOP BUILD when ntfy fires.

---

## Thread routing (agent-initiated — not founder ritual)

| Intent | Who opens | Notes |
|--------|-----------|-------|
| Factory / relay (degraded) | **Agent** in Cursor when automation blocked | `OPERATOR_STATUS` → burst → workers — founder does not open this routinely |
| Product / strategy / SELECTION | **Founder** when steering | Founder charter starter — **no** `OPERATOR_STATUS` |
| One product slice (degraded BUILD) | **Agent** | `ide_build` + starter — not founder paste |

When founder charter work needs execution → runtime or agent thread owns it — **does not** ask founder to run relay.

---

## Cadence tags ([`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md))

| Tag | Meaning |
|-----|---------|
| `founder` | Judgment or external world — founder only |
| `agent` | Automation or agent thread runs and reports |
| `digest-only` | Monday ntfy summary; no action unless founder opts in |

Agents must not convert `agent` or `digest-only` rows into founder todo lists in unrelated threads.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | v1 — founder vs agent surface SSOT; reply contract; cadence tags |
| 2026-07-01 | v1.1 — runtime automation SSOT; founder never opens factory threads; degraded-mode table |
