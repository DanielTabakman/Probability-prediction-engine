# Autobuilder Git Publication V2

## Decision

GitHub is a durable change plane, not a live runtime-state bus.

The supported publication lifecycle is:

```text
one selected chapter
→ one stable chapter branch
→ one pull request
→ repeated commits on that branch
→ evidence and checks
→ merge
→ closeout
```

Timestamped `ops/loop-publish-*`, `ops/vm-mirror-*`, and `ops/closeout-*` publication is legacy behavior and is disabled by default.

## Runtime state

Live VM phase state is written to:

```text
artifacts/control_plane/VM_OPERATOR_PHASE.json
```

This path is gitignored. Direct SSH/status reads are authoritative. ntfy is used for meaningful transitions and stuck conditions. Phase refreshes must never create commits, branches, or pull requests.

The former tracked path `docs/SOP/VM_OPERATOR_PHASE.json` is removed. Code may read it only as a temporary compatibility fallback when operating against an older checkout.

## Legacy publisher break glass

The old publisher requires both variables:

```text
PPE_GIT_AUTONOMOUS_WRITES=legacy-unsafe
PPE_ALLOW_LEGACY_GIT_PUBLISH=1
```

Do not set these during normal operation.

`PPE_GIT_AUTONOMOUS_WRITES=1` no longer re-enables legacy publication.

## Chapter publication

Use:

```bat
ppe_chapter_publish.cmd ^
  --chapter-id MSOS-MCD ^
  --title "MSOS: Minimum Credible Demo" ^
  --body "Bounded chapter delivery" ^
  --create-branch
```

The wrapper sets `PPE_CHAPTER_PUBLISH=1` for the explicit invocation.

The publisher:

- uses a stable `chapter/<chapter-id>` branch when starting from `main`;
- updates an existing PR for the chapter instead of replacing it;
- adds a durable chapter marker to the PR body;
- rejects runtime-only paths;
- skips an already-published semantic diff;
- blocks duplicate head SHAs;
- blocks multiple PRs for one chapter;
- blocks when more than five autonomous PRs are open;
- blocks when three autonomous PRs were created within 30 minutes;
- does not add automerge by default.

## Context closeout

`ppe_context_closeout_ship.py` commits closeout work to the active chapter branch and delegates publication to the chapter publisher. It does not create timestamped recovery branches or replacement PRs.

Chapter identity is resolved in this order:

1. `PPE_ACTIVE_CHAPTER_ID`;
2. preflight chapter fields;
3. `ACTIVE_PHASE_MANIFEST.json`;
4. current non-main branch;
5. stable `context-closeout` fallback.

## Backlog cleanup

Preview safe cleanup:

```bat
ppe_autobuilder_pr_cleanup.cmd --json
```

Apply only safe classifications:

```bat
ppe_autobuilder_pr_cleanup.cmd --apply --json
```

Optionally delete closed remote branches:

```bat
ppe_autobuilder_pr_cleanup.cmd --apply --delete-branches --json
```

Automatic cleanup is limited to:

- older PRs with an exact duplicate open head SHA;
- VM mirror PRs;
- timestamped loop/closeout PRs containing only runtime-state paths.

Mixed or unique diffs require deliberate reconciliation.

## Verification

After updating and restarting the loop host, verify the observation window:

```bat
ppe_autobuilder_churn_verify.cmd --hours 24 --json
```

Acceptance requires:

- zero timestamped loop/mirror/closeout PRs in the window;
- no tracked `docs/SOP/VM_OPERATOR_PHASE.json` drift;
- one open PR maximum for the active chapter;
- repeated status refreshes producing no tracked-file diff.

## Operator restart sequence

On the loop host:

```bat
git checkout main
git pull --ff-only origin main
set PPE_GIT_AUTONOMOUS_WRITES=
set PPE_ALLOW_LEGACY_GIT_PUBLISH=
```

Then stop and restart the headless operator/supervisor so already-imported Python modules are replaced by the new code.
