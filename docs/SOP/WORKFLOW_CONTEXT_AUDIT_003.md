# Workflow Context Audit 003 — ChatGPT/GitHub/Codex context economy

**Status:** implementation evidence for issue [#5274](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5274).  
**Plane:** CONTROL-PLANE. **Posture:** advisory; character-derived token estimates are not billing.  
**Baseline ref:** GitHub `main` at `56e69d3539059b9e13643bb9eb87029f2d4f861f` (2026-07-11).

## 1. Scope and evidence boundary

This audit extends the existing Cursor-focused token monitor to deterministic repository surfaces used by the ChatGPT Project → GitHub → Codex workflow. It does not estimate proprietary hidden context, subscription usage, or API billing.

The implementation runtime had GitHub file/branch/PR access but no repository checkout, `gh`, intended operator-machine config, or generated `TOKEN_AUDIT_LATEST` artifact. Therefore the existing operator-machine command `token_audit.cmd --stdout` could not be executed honestly before editing. That missing baseline is carried as an explicit validation gap; it is not replaced with invented numbers.

The existing Cursor audit in `scripts/ppe_token_audit.py` is preserved. `token_audit.cmd` now composes it with `scripts/ppe_context_surface_audit.py`, so the next operator-machine run produces both surfaces without replacing prior metrics.

## 2. Fresh deterministic baseline

The compact ChatGPT Project text and role contracts were measured directly from the issue-listed canon on `main`.

| Fixed startup surface | Components | Chars | Estimated tokens |
|---|---|---:|---:|
| ChatGPT Project instructions | fenced text in `CHATGPT_PROJECT_STARTER.md` | 951 | ~238 |
| Founder setup | Project instructions + founder role contract | 1,241 | ~311 |
| Charter | Project instructions + charter role contract | 1,213 | ~304 |
| Codex implementation handoff | Project instructions + Codex role contract | 1,258 | ~315 |
| Review/reconciliation | Project instructions + review role contract | 1,222 | ~306 |

Estimates use `ceil(chars / 4)`. Variable program docs, GitHub issues, PRs, logs, and conversation history are excluded from the fixed bundle and measured separately when present.

### Existing route baseline

| Request/surface | Before on `main` | Avoidable cost |
|---|---|---|
| Generic `founder charter` / `charter thread` / `topic thread` | `PHASE_CHAPTER_BACKLOG.json` + `ACTIVE_PRODUCT_DIRECTION.json` fixed-loaded | Broad queue/direction state loaded before a topic exists |
| Generic SOP discovery | `AGENT_ROUTING_V1.md` + `CHAPTER_DOC_INDEX.json` fixed-loaded | Full generated chapter index loaded when a direct route may suffice |
| Operator role | `OPERATOR_STATUS.md` + `AGENT_CONTINUITY_BRIEF.md` + `ACTIVE_PRODUCT_DIRECTION.json` fixed-loaded | Generated continuity is repeated even when stale or redundant |
| Generated continuity brief | Told agents to load it first | Embedded HEAD was stale, active relay/sprint/plan fields were blank, and a machine-specific absolute path was present |

## 3. Largest avoidable costs

1. **Broad state before scope.** Generic founder/charter phrases triggered selection/backlog state even though the control-plane contract says a charter thread should load one relevant program.
2. **Generated continuity treated as authority-looking startup context.** The brief was stale/incomplete relative to `main` but still instructed agents to load it first.
3. **Always-loaded index without demonstrated need.** `CHAPTER_DOC_INDEX.json` was loaded for generic discovery rather than only for chapter lookup.
4. **No cross-surface accounting.** The monitor described perpetual token oversight while measuring Cursor rules/starters and worker routing only.

## 4. Changes made

### Deterministic cross-surface audit

Added `scripts/ppe_context_surface_audit.py` to measure:

- fenced ChatGPT Project instructions;
- founder, charter, Codex implementation, and review role contracts;
- fixed startup bundles;
- full control-plane/routing/continuity/index/backlog/direction file sizes;
- generated continuity freshness, completeness, and portability;
- labeled `ceil(chars / 4)` token approximations and explicit unmeasurable categories.

It writes `CONTEXT_SURFACE_AUDIT_LATEST.md` and `.json` beside the existing token artifacts. `token_audit.cmd` runs the preserved Cursor audit first, then this report.

### Routing correction

Added `scripts/context_economy_routing.py` and routed public `resolve_sop.py` role/topic resolution through it.

- Generic founder setup loads the control-plane role contract only; Project instructions are already present.
- Generic charter phrases require one named program, charter, or issue and fixed-load no backlog/direction state.
- Explicit selection/closeout phrases retain the existing backlog/direction route.
- SOP discovery moves `CHAPTER_DOC_INDEX.json` to on demand.
- Operator routing moves generated continuity to on demand and adds a freshness warning.
- Chapter, module, and search resolution remain on the existing core paths.

The large discovery catalog remains intact to avoid an unrelated refactor. The overlay corrects the public CLI boundary while preserving explicit legacy routes.

### Generated-context safe behavior

A generated continuity brief is safe to load first only when:

1. its embedded HEAD matches the current checkout;
2. active relay, sprint, and plan fields are populated;
3. it does not require a machine-specific absolute path.

Otherwise agents use GitHub `main` plus current operator status/direction as applicable, disclose the gap, and regenerate through `apply_control_closeout_v1`.

`AGENT_CONTINUITY_BRIEF.md` itself was intentionally not edited because open PR #5279 already owns that generated path.

## 5. Before/after measurements

| Route | Before fixed-loaded docs | After fixed-loaded docs | Change |
|---|---:|---:|---:|
| Generic founder setup | 2 broad state docs | 1 control-plane contract | Removes backlog + active direction from startup |
| Generic charter/topic thread | 2 broad state docs | 0 repo state docs until topic is named | Removes both broad state docs |
| SOP discovery | 2 docs including generated index | 1 routing canon; index on demand | Removes index from default load |
| Operator role | 3 docs including generated continuity | 2 current state docs; continuity on demand | Removes unsafe generated default |

The fixed role bundles remain approximately 304–315 estimated tokens before variable task context. The change targets unrelated variable documents rather than weakening the role contract, evidence requirements, or disagreement detection.

The branch audit will additionally report exact full-file character sizes from the checkout. Those values are generated rather than copied into canon so they stay current as files change.

## 6. Validation

Added tests for:

- generic founder routing excludes backlog/direction;
- generic charter routing requires a named scope;
- explicit selection work preserves state routing;
- chapter index is on demand for SOP discovery;
- operator continuity is freshness-gated;
- project/role/fixed-bundle character accounting;
- stale/incomplete/machine-specific continuity is unsafe;
- fresh, complete, portable continuity is safe.

Target validation:

```bat
token_audit.cmd --stdout
python -m pytest -q tests -k "token or sop_discovery or context"
python scripts/resolve_sop.py --role operator --json
python scripts/resolve_sop.py --role charter --json
python scripts/resolve_sop.py --topic "founder charter" --json
python scripts/resolve_sop.py --topic "charter thread" --json
python scripts/resolve_sop.py --topic "token budget" --json
```

## 7. Recommended recurring thresholds

| Surface | Recommended default |
|---|---:|
| ChatGPT Project instructions | ≤1,500 chars |
| One role contract | ≤800 chars |
| Fixed Project + role startup bundle | ≤2,500 chars |
| Generated continuity brief | ≤4,000 chars and fresh/complete/portable |
| Generic founder/charter state files | 0 until one program/issue is named |
| Chapter index/backlog/status | On demand unless the named task requires it |

These thresholds are advisory until repeated operator-machine audits establish a stable trend.

## 8. What remains unmeasurable or pending

- proprietary ChatGPT system/Project context not represented in the repository;
- exact ChatGPT, Codex, Cursor, subscription, or API billing;
- operator-local configuration and build-worker events absent from this runtime;
- variable issue/PR/program/log/conversation content;
- a fresh intended-operator-machine `token_audit.cmd --stdout` result.

The last item must be attached to the draft PR or run immediately after checkout; until then, acceptance criterion A remains an explicit evidence gap rather than a claimed pass.

## 9. Coordination status

```text
COORDINATION STATUS
Agreement: partial
Compared: issue #5274, GitHub main at 56e69d3539059b9e13643bb9eb87029f2d4f861f, listed canon, routing code, and open PR ownership
Disagreement: generated continuity says load first while its embedded state is stale/incomplete relative to main
Evidence gap: no intended-operator-machine token_audit baseline was available in this implementation runtime
Ownership overlap: PR #5279 edits AGENT_CONTINUITY_BRIEF.md; this change leaves that generated file untouched
Risk if unresolved: stale generated state can displace current canon and cross-surface overhead can remain invisible
Recommended default: merge only after relevant tests pass and an operator-machine token_audit --stdout result is attached or acknowledged as follow-up evidence
Founder decision required: no
```
