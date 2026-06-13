# GitHub: zero-touch merge and ship

Purpose: define how changes reach **`main` without a human merge click** when automated tests pass, and how production deploy fits in (manual step by design).

## Philosophy

- **Human in the loop for design and repair, not for routine merge.** The steward defines priorities, slice scope, and recovery when something is wrong—not a standing approval gate on every green PR.
- **Merge when checks pass.** Use GitHub **auto-merge** on pull requests so the platform merges as soon as required status checks succeed (no manual “Merge” click for the common case).
- **Ship on `main`.** After merge, [deploy-vps.yml](../../.github/workflows/deploy-vps.yml) runs on pushes to **`main`**; the VPS reconciles with GitHub. See [PRODUCTION_DEPLOY_PROTOCOL.md](PRODUCTION_DEPLOY_PROTOCOL.md).

This doc is the **GitHub-side contract**. Relay/orchestrator promotion still produces a branch and PR (or equivalent); this layer completes the path to **`main`** and the live site.

## Public repository

This repo is **public** — standard Linux Actions runners are **free**. Uptime checks run every **30 minutes** (not every 5) to avoid unnecessary runner churn.

## GitHub Free and **private** repositories

Branch protection and repository rulesets from the **REST API** may return **403** (“Upgrade to GitHub Pro or make this repository public”). **`allow_auto_merge`** may also stay **false** via API on private free repos. Options:

1. **GitHub Pro / Team** (or org plan) for this repo, or  
2. **Public** repo if that is acceptable for the project, or  
3. **Manual** setup in the GitHub **Settings** UI (branch rules / pull requests); the scripted helper still prints guidance when the API is blocked.  
4. **Merge on green (Actions workaround)** — keep the repo private on Free and use two workflows:
   - [`.github/workflows/label-pr-automerge.yml`](../../.github/workflows/label-pr-automerge.yml) — on each PR to **`main`** (non-draft, same-repo branch), creates the **`automerge`** label if missing and applies it (**no manual label**).
   - [`.github/workflows/merge-on-green.yml`](../../.github/workflows/merge-on-green.yml) — after **CI** *or* **Label PR automerge** completes successfully, merges the PR when the latest **CI** run for the PR head is **success** and the **`automerge`** label is present (squash). Listening to both removes label-vs-CI ordering races.

### Merge on green (Actions workaround)

Use this when **Allow auto-merge** is greyed out (typical for **private** repos on **GitHub Free**).

1. **One-time:** set **Settings → Actions → General → Workflow permissions** to **Read and write** (see below).  
2. Merge these workflow files to **`main`** so they run on the default branch.  
3. Open a **non-draft** PR to **`main`** from a branch in this repo — **`automerge`** is applied automatically; when **CI** is green, **Merge on green** squash-merges.  
4. **Deploy VPS** runs on push to **`main`**.

**Draft PRs:** no **`automerge`** label while draft; when you mark **Ready for review**, the label workflow runs again and the usual CI → merge path applies.

**Why a label:** merge-on-green only merges PRs that carry **`automerge`**, so stray or fork PRs are not merged by mistake (fork heads are skipped by the label workflow).

**Permissions:** Uses the default **`GITHUB_TOKEN`** with `contents: write` and `pull-requests: write` (declared in the workflow). The workflow file must live on the **default branch** to receive `workflow_run` events.

If merges fail with **403** or **Resource not accessible**, set **Settings → Actions → General → Workflow permissions** to **Read and write permissions** (and allow GitHub Actions to create and approve pull requests, if GitHub shows that sub-option).

## Preconditions (repository)

1. **CI workflow on `main`:** [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) must exist on the default branch so status checks exist to require.
2. **Deploy workflow and secrets:** [GITHUB_ACTIONS_VPS_DEPLOY.md](../DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md) — otherwise merges update GitHub but not the VPS.

## One-time GitHub settings (steward / admin)

Complete after the first successful **CI** run on `main` (so the check name appears in the branch rule UI).

### Scripted setup (recommended)

From the repo root, after [GitHub CLI](https://cli.github.com/) is installed and you are logged in (`gh auth login -h github.com -p https -w`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/enable_github_zero_touch.ps1
```

This enables **Allow auto-merge** and creates or updates a ruleset named **`PPE zero-touch main`** for `refs/heads/main` (PR required with **0** approvals, required checks **`CI / pytest`** and **`CI / docker_entrypoint`**, no force-push). Re-run the script anytime to refresh that ruleset.

### Repository

- **Settings → General → Pull Requests:** enable **Allow auto-merge** (the script above does this via API; confirm in the UI if you like).

### Branch protection rule for `main`

**Settings → Rules → Rulesets** (or **Branches → Branch protection rules**, depending on GitHub UI).

Recommended for the stated policy:

| Rule | Recommendation |
|------|----------------|
| Require a pull request before merging | **On** (so every production change has a PR trail; direct pushes to `main` bypass checks). |
| Require status checks to pass before merging | **On** — require **`CI / pytest`** and **`CI / docker_entrypoint`** (workflow **CI**, jobs **pytest** and **docker_entrypoint**). |
| Require branches to be up to date before merging | **On** if you want a strict linear gate; pairs well with **merge queue** (optional). |
| Require approvals | **Off** for “no human in merge path when green” (steward verifies on the site when they choose, not as a merge blocker). |
| Allow administrators to bypass | **Off** if you want the same rules for everyone including admins. |
| Restrict who can push | Limit pushes to `main` to automation accounts or nobody (PR-only), if your org supports it. |

### Merge button behavior

- When opening or updating a PR, enable **Enable auto-merge** (squash, merge, or rebase—pick one convention for the repo and stick to it).
- Bots or the orchestrator can use the [GitHub REST API](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#enable-automatic-merging-for-a-pull-request) to enable auto-merge if they use credentials with `pull_requests: write` (and contents as required by your merge method).

### Optional: merge queue

If you turn on a **merge queue** for `main`, add the `merge_group` trigger to CI (already present in `ci.yml`) and require the queue in branch protection. This serializes merges and re-runs checks on the combined head—stronger for high churn, slightly slower.

## Operational flow (routine)

**Path A — native auto-merge** (public repo, Pro, or UI allows it):

1. Work lands on a **feature branch** (worker/orchestrator or human).
2. Open a PR to **`main`**; enable **auto-merge**.
3. **`CI / pytest`** and **`CI / docker_entrypoint`** run; when green, GitHub merges without further human action.
4. **Deploy VPS** runs on the push to **`main`**; post-deploy smoke when you want assurance ([DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5).

**Path B — private Free (greyed-out auto-merge):**

1. Open a PR to **`main`** from a branch in this repo (non-draft). **`automerge`** is added by **Label PR automerge**; **CI** runs; **Merge on green** merges after both are satisfied (no **Enable auto-merge** button).  
2. **Deploy VPS** runs on the push to **`main`**; post-deploy smoke when you want ([DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5).

## Troubleshooting (steward)

| Symptom | What to check |
|--------|----------------|
| Auto-merge not available | Repo setting **Allow auto-merge**; branch protection may require incompatible rules. **Private Free:** use label **`automerge`** + workflow **Merge on green** ([GITHUB_ZERO_TOUCH_MERGE.md](GITHUB_ZERO_TOUCH_MERGE.md)). |
| PR stuck “waiting on checks” | Confirm `ci.yml` is on `main` and required check names match **`CI / pytest`** and **`CI / docker_entrypoint`**. |
| Checks green but no merge | Conflicts with base branch; or latest **CI** on the PR head is not **success** yet; or PR is **draft**. **Private Free:** confirm **Merge on green** ran (Actions tab) and **Workflow permissions** allow read/write. |
| Merged but site old | [PRODUCTION_DEPLOY_PROTOCOL.md](PRODUCTION_DEPLOY_PROTOCOL.md) §D; confirm **Deploy VPS** run for that commit. |

## Related

- [RELAY_ORCHESTRATOR_RUNBOOK_V1.md](RELAY_ORCHESTRATOR_RUNBOOK_V1.md) — slice/phase artifacts; **Shipping (GitHub)** subsection.  
- [PRODUCTION_DEPLOY_PROTOCOL.md](PRODUCTION_DEPLOY_PROTOCOL.md) — VPS and `main` as source of truth.  
- [README](../../README.md) — commit/merge test gates; CI runs **ruff + full pytest** (`CI / pytest`) and **Docker entrypoint smoke** (`CI / docker_entrypoint`).
- [COMMIT_POLICY_V1.md](COMMIT_POLICY_V1.md) — canonical local gate before pushable commits.
