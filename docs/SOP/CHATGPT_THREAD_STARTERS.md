# ChatGPT thread starters

## Founder setup / collaboration

```text
Founder collaboration/setup thread. THREAD_ROLE: founder_charter.
GitHub is the source of truth. Relay: off.
Load docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md and docs/SOP/FOUNDER_COLLABORATION_CHARTER_V1.md.
Do not implement product code. Record accepted operating changes in GitHub.
```

## Charter / product topic

```text
Charter thread. THREAD_ROLE: charter.
Topic: <topic>.
GitHub is the source of truth. Relay: off.
Read only the relevant program and code paths. Surface conflicts; do not silently resolve canon.
Produce or update the charter and a bounded implementation handoff.
```

## Implementation

```text
Implementation thread. THREAD_ROLE: codex_build.
Implement only the linked GitHub issue or task packet.
Do not change product direction or acceptance criteria.
Before editing, report ownership overlap and disagreement with the charter.
Open a draft PR and include fresh validation evidence.
```

## Review / reconciliation

```text
Review thread. THREAD_ROLE: review.
Review PR <number> against its charter, task packet, and acceptance criteria.
Do not assume the implementing agent is correct.
Return a COORDINATION STATUS block and identify canon, evidence, ownership, implementation, or priority conflict.
```
