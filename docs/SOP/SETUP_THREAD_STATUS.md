# Setup thread status

**Purpose:** Human-readable checkpoint for the initial ChatGPT + GitHub + Codex control-plane setup.

## Established

- GitHub is the canonical source of truth.
- Regular Chat owns chartering, alignment, documentation, bounded repository review, and PR reconciliation.
- Codex owns implementation, tests, commands, and runtime debugging.
- Agent disagreements must be surfaced through `COORDINATION_STATUS_TEMPLATE.md`.
- Automatic Google Docs synchronization is retired; manual fallback remains pending a dependency audit.
- One ChatGPT Project, **PPE / MSOS Control Plane**, groups founder, charter, implementation, and review threads without replacing GitHub canon.

## Next setup work

1. Review and merge the control-plane PR.
2. Create the ChatGPT Project and paste `CHATGPT_PROJECT_STARTER.md` into its instructions.
3. Move or recreate this setup conversation inside that Project.
4. Open the first focused charter thread using `CHATGPT_THREAD_STARTERS.md`.
5. Audit remaining Google Docs scripts, secrets, and references before deletion.
