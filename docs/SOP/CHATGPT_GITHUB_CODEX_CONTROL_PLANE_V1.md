# ChatGPT + GitHub + Codex control plane v1

**Plane:** CONTROL-PLANE  
**Status:** Active operating contract  
**Canonical home:** GitHub repository  
**Purpose:** Separate founder alignment from implementation while forcing agent disagreement, ownership conflict, and evidence gaps into the open.

## Core operating model

| Surface | Owns | Does not own |
|---|---|---|
| **Founder** | Product direction, priorities, definition of done, canon conflicts, external-world decisions | Git mechanics, test commands, routine implementation choices |
| **ChatGPT regular Chat** | Chartering, product reasoning, repository reading, documentation, task decomposition, PR review, disagreement detection | Runtime claims without evidence, silent implementation, autonomous test loops |
| **Codex / implementation agents** | Code changes, commands, tests, runtime debugging, bounded refactors, implementation PRs | Product canon, silent priority changes, redefining done |
| **GitHub** | Canonical documents, code, history, issues, branches, PRs, accepted decisions | Private chat-only conclusions |
| **ChatGPT Project** | Organizes related chats and working context | Canonical product truth |

**Hard rule:** A conclusion that changes product direction, architecture, responsibility, acceptance criteria, or agent behavior is not canonical until it is recorded in GitHub.

## Source-of-truth precedence

1. Accepted files on the default GitHub branch.
2. An explicitly approved open PR for work not yet merged.
3. Evidence from current code, tests, deployment, or reproducible commands.
4. Current thread reasoning and proposals.
5. Historical chat, Google Docs, or stale generated mirrors.

Google Docs is a legacy/manual fallback only. It must not override GitHub and must not be treated as an active control plane.

## Thread model

Create a new thread when the optimization target or agent role changes. Do not create a new thread for every small action.

### 1. Founder setup and collaboration

Use for the operating system itself: roles, alerts, token use, documentation rules, and cross-agent coordination.

```text
Founder collaboration/setup thread. THREAD_ROLE: founder_charter.
GitHub is the source of truth. Relay: off.
Load docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md and docs/SOP/FOUNDER_COLLABORATION_CHARTER_V1.md.
Do not implement product code. Record accepted operating changes in GitHub.
```

### 2. Charter or product topic

Use for product design, architecture, UX, data programs, research, and acceptance criteria.

```text
Charter thread. THREAD_ROLE: charter.
Topic: <topic>.
GitHub is the source of truth. Relay: off.
Read only the relevant program and code paths. Surface conflicts; do not silently resolve canon.
Produce or update the charter and a bounded implementation handoff.
```

### 3. Codex implementation

Use for a bounded implementation, tests, runtime work, or debugging.

```text
Implementation thread. THREAD_ROLE: codex_build.
Implement only the linked GitHub issue or task packet.
Do not change product direction or acceptance criteria.
Before editing, report ownership overlap and any disagreement with the charter.
Open a draft PR and include evidence from tests or runtime checks.
```

### 4. Review and reconciliation

Use after an implementation PR or when agents may disagree.

```text
Review thread. THREAD_ROLE: review.
Review PR <number> against its charter, task packet, and acceptance criteria.
Do not assume the implementing agent is correct.
Return a Coordination Status block and identify any canon, evidence, ownership, or implementation conflict.
```

## Mandatory coordination status

Whenever one agent reviews, continues, or depends on another agent's work, it must return this block:

```text
COORDINATION STATUS
Agreement: aligned | partial | conflict | unknown
Compared: <charter / issue / PR / commit / files>
Disagreement: <none or concise statement>
Evidence gap: <none or missing proof>
Ownership overlap: <none or overlapping paths/state>
Risk if unresolved: <none or consequence>
Recommended default: <one action>
Founder decision required: yes | no
```

An agent must not report `aligned` unless it compared the work to an identifiable GitHub artifact or current evidence.

## Conflict classes

| Conflict | Meaning | Default response |
|---|---|---|
| **Canon conflict** | Product or architecture documents prescribe different outcomes | Stop the disputed decision; show both outcomes; founder decides |
| **Implementation conflict** | Code differs from accepted intent or acceptance criteria | Keep PR draft; recommend a correction |
| **Evidence conflict** | Agents disagree about whether something works or is complete | Prefer fresh reproducible evidence; mark unknown until verified |
| **Ownership conflict** | Two agents may edit the same files, branch, queue, manifest, or deployment state | One writer only; second agent reviews or waits |
| **Priority conflict** | Agent starts work outside the selected order | Park the work and return to the selected task |

## No-silent-fighting rules

1. Agents may disagree; they may not conceal disagreement behind a confident summary.
2. No agent may rewrite canon merely to match its implementation.
3. No agent may declare another agent wrong without naming the conflicting artifact or evidence.
4. If two agents intend to modify overlapping paths or shared control-plane state, only one remains the writer.
5. Technical disagreements that do not change product outcomes are resolved by evidence and the smallest reversible implementation.
6. Product, priority, definition-of-done, or canon disagreements are presented to the founder in outcome language with one recommended default.
7. Unresolved disagreements stay visible in the PR, issue, or coordination block until resolved.

## GitHub handoff packet

Every implementation request should provide:

```markdown
## Goal

## Why this matters

## Canon / relevant documents

## Relevant code paths

## Current behavior

## Required behavior

## Constraints

## Non-goals

## Acceptance criteria

## Validation commands or evidence

## Ownership / overlap warning
```

The implementation agent should not rediscover the whole repository when this packet is sufficient.

## Write policy

- Charter and documentation work may be performed from regular Chat through the GitHub connection.
- Material control-plane changes use a branch and draft PR by default.
- Product code implementation belongs in a bounded implementation branch and PR.
- Direct writes to the default branch are reserved for explicitly authorized trivial or emergency changes.
- Every PR states what changed, why, validation evidence, and its Coordination Status.

## Google Docs retirement

- GitHub is authoritative for product canon, control-plane state, and documentation.
- Scheduled Google Docs synchronization is disabled.
- The existing Google Docs workflow may remain manually dispatchable as a temporary archival or export fallback.
- Historical Google Docs are references only and must be labeled stale unless reconfirmed against GitHub.
- Secrets and sync scripts may be removed later after a separate dependency audit confirms nothing still relies on them.

## Project layout outside GitHub

Use one ChatGPT Project named **PPE / MSOS Control Plane**.

Keep these chats inside it:

- Founder setup / collaboration
- One charter thread per substantial product topic
- One review thread per material PR or implementation arc

Codex implementation threads may also live there, but their durable handoff and result must be a GitHub issue or PR. Do not use the ChatGPT Project as a replacement for repo documentation.

## Decision rule

When unsure where work belongs:

- **What should we build, why, or what does done mean?** → Charter thread.
- **How does the current repository work?** → Regular Chat repository review.
- **Write or revise canonical documentation?** → Regular Chat + GitHub draft PR.
- **Run, test, debug, or implement across files?** → Codex implementation.
- **Agents disagree or evidence is unclear?** → Review/reconciliation thread with Coordination Status.
