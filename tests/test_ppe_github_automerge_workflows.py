from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LABEL_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "label-pr-automerge.yml"
MERGE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "merge-on-green.yml"
ZERO_TOUCH_DOC = REPO_ROOT / "docs" / "SOP" / "GITHUB_ZERO_TOUCH_MERGE.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _yaml(path: Path) -> dict:
    data = yaml.safe_load(_read(path))
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def test_label_workflow_requires_explicit_marker_and_safe_pr_shape() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "const marker = '<!-- ppe-automerge: true -->';" in source
    assert "if (eventPr.draft)" in source
    assert "Fork or foreign head" in source
    assert "currentPr.state !== 'open' || currentPr.draft || currentPr.merged" in source
    assert "currentPr.head.sha !== eventPr.head.sha" in source
    assert "lost explicit automerge marker before labeling" in source
    assert "labeledPr.head.sha !== currentPr.head.sha" in source
    assert "does not have automerge label after label step" in source


def test_label_workflow_permissions_and_concurrency_are_bounded() -> None:
    workflow = _yaml(LABEL_WORKFLOW)

    assert workflow["permissions"] == {
        "contents": "read",
        "pull-requests": "write",
        "issues": "write",
        "actions": "write",
    }
    assert workflow["concurrency"] == {
        "group": "label-pr-automerge-${{ github.event.pull_request.number }}",
        "cancel-in-progress": False,
    }


def test_label_workflow_queries_exact_head_pull_request_ci_runs() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "github.paginate(github.rest.actions.listWorkflowRuns" in source
    assert "workflow_id: 'ci.yml'" in source
    assert "head_sha: labeledPr.head.sha" in source
    assert "event: 'pull_request'" in source
    assert ".filter((run) => run.head_sha === labeledPr.head.sha && run.event === 'pull_request')" in source
    assert ".sort((a, b) => {" in source
    assert "return byTime || b.id - a.id;" in source


def test_label_workflow_requires_current_pr_head_and_base_association() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "const classifyRunContext = (run, pr) => {" in source
    assert "const refs = run.pull_requests || [];" in source
    assert "if (refs.length !== 1)" in source
    assert "missing PR association" in source
    assert "ambiguous PR associations" in source
    assert "ref.number !== pr.number" in source
    assert "head.sha !== pr.head.sha" in source
    assert "head.ref && head.ref !== pr.head.ref" in source
    assert "base.sha !== pr.base.sha" in source
    assert "base.ref && base.ref !== pr.base.ref" in source


def test_label_workflow_excludes_stale_context_runs_from_selection() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "const classifiedRuns = exactRuns.map((run) => ({" in source
    assert "currentContextRuns = classifiedRuns" in source
    assert ".filter((item) => item.context.current)" in source
    assert "staleContextRuns = classifiedRuns" in source
    assert ".filter((item) => !item.context.current)" in source
    assert "Stale-context exact-head CI run" in source
    assert "activeRuns = currentContextRuns.filter" in source
    assert "const latest = currentContextRuns[0];" in source


def test_label_workflow_active_ci_guard_prevents_duplicate_reruns() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "const activeStatuses = new Set(['queued', 'in_progress', 'requested', 'waiting', 'pending']);" in source
    assert "if (activeRuns.length > 1)" in source
    assert "Multiple active current-context exact-head CI runs" in source
    assert "if (activeRuns.length === 1)" in source
    assert "will own Merge on Green" in source
    active_block = source.split("if (activeRuns.length === 1)", maxsplit=1)[1].split(
        "const latest = currentContextRuns[0];",
        maxsplit=1,
    )[0]
    assert "reRunWorkflow" not in active_block


def test_label_workflow_only_reruns_completed_successful_exact_head_ci() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "if (!latest)" in source
    assert "normal ${context.payload.action} CI may still be materializing" in source
    assert "no current-context run matches" in source
    assert "base advanced or CI association cannot be proven" in source
    assert "Refresh the PR branch against current main" in source
    assert "Late automerge opt-in" in source
    assert "has no current-context exact-head CI run to rerun" in source
    assert "latest.status !== 'completed' || latest.conclusion !== 'success'" in source
    assert "refusing automatic rerun" in source
    assert "github.rest.actions.reRunWorkflow" in source
    assert "run_id: latest.id" in source
    assert "Requested full rerun of current-context exact-head CI run" in source


def test_label_workflow_final_refetches_pr_before_rerun() -> None:
    source = _read(LABEL_WORKFLOW)

    final_refetch = source.split("const { data: finalPr } = await github.rest.pulls.get", maxsplit=1)[1]
    pre_rerun_block = final_refetch.split("const response = await github.rest.actions.reRunWorkflow", maxsplit=1)[0]
    assert "pull_number: labeledPr.number" in pre_rerun_block
    assert "finalPr.state !== 'open' || finalPr.draft || finalPr.merged" in pre_rerun_block
    assert "lost explicit automerge marker before CI rerun" in pre_rerun_block
    assert "lost automerge label before CI rerun" in pre_rerun_block
    assert "finalPr.head.sha !== labeledPr.head.sha || finalPr.head.ref !== labeledPr.head.ref" in pre_rerun_block
    assert "finalPr.base.sha !== labeledPr.base.sha || finalPr.base.ref !== labeledPr.base.ref" in pre_rerun_block


def test_label_workflow_never_merges_or_dispatches_deploy() -> None:
    source = _read(LABEL_WORKFLOW)

    assert "pulls.merge" not in source
    assert "merge_method" not in source
    assert "createWorkflowDispatch" not in source
    assert "deploy-vps.yml" not in source
    assert "updateBranch" not in source
    assert "updateBranchForPullRequest" not in source
    assert "merge_upstream" not in source


def test_merge_on_green_authority_still_only_follows_ci_completion() -> None:
    workflow = _yaml(MERGE_WORKFLOW)
    source = _read(MERGE_WORKFLOW)

    assert workflow["on"] == {"workflow_run": {"workflows": ["CI"], "types": ["completed"]}}
    assert "github.event.workflow_run.conclusion == 'success'" in source
    assert "github.event.workflow_run.event == 'pull_request'" in source
    assert "run.name !== 'CI'" in source
    assert "label.name === 'automerge'" in source
    assert "github.rest.actions.getWorkflowRun" in source
    assert "exactRun.conclusion !== 'success'" in source
    assert "merge_method: 'squash'" in source


def test_merge_on_green_has_no_branch_name_fallback() -> None:
    source = _read(MERGE_WORKFLOW)

    assert "github.rest.pulls.list" not in source
    assert "head: `${owner}:${run.head_branch}`" not in source
    assert "run.head_branch && run.head_branch !== defaultBranch" not in source


def test_merge_on_green_requires_exactly_one_pr_association() -> None:
    source = _read(MERGE_WORKFLOW)

    assert "const prRefs = run.pull_requests || [];" in source
    assert "if (prRefs.length !== 1)" in source
    assert "must have exactly one explicit PR association" in source
    assert "found ${prRefs.length}" in source


def test_merge_on_green_requires_current_pr_head_and_base_association() -> None:
    source = _read(MERGE_WORKFLOW)

    assert "const classifyRunContext = (workflowRun, pr) => {" in source
    assert "const refs = workflowRun.pull_requests || [];" in source
    assert "missing PR association" in source
    assert "ambiguous PR associations" in source
    assert "ref.number !== pr.number" in source
    assert "head.sha !== pr.head.sha" in source
    assert "head.ref && head.ref !== pr.head.ref" in source
    assert "base.sha !== pr.base.sha" in source
    assert "base.ref && base.ref !== pr.base.ref" in source
    assert "run base ${base.sha || 'missing'} current base ${pr.base.sha}" in source


def test_merge_on_green_exact_workflow_run_is_fetched_and_checked_by_id() -> None:
    source = _read(MERGE_WORKFLOW)

    assert "const { data: exactRun } = await github.rest.actions.getWorkflowRun" in source
    assert "run_id: run.id" in source
    assert "exactRun.id !== run.id" in source
    assert "exactRun.name !== 'CI'" in source
    assert "exactRun.event !== 'pull_request'" in source
    assert "exactRun.status !== 'completed'" in source
    assert "exactRun.conclusion !== 'success'" in source
    assert "exactRun.head_sha !== run.head_sha" in source
    assert "exactRun.run_attempt && run.run_attempt" in source


def test_merge_on_green_exact_run_association_must_be_current_context() -> None:
    source = _read(MERGE_WORKFLOW)

    assert "requireCurrentContext(run, pr, 'workflow_run event association')" in source
    assert "requireCurrentContext(exactRun, pr, 'exact workflow-run association')" in source
    assert "requireCurrentContext(run, finalPr, 'final workflow_run event association')" in source
    assert "requireCurrentContext(exactRun, finalPr, 'final exact workflow-run association')" in source


def test_merge_on_green_rechecks_marker_label_and_mergeability() -> None:
    source = _read(MERGE_WORKFLOW)

    assert "const marker = '<!-- ppe-automerge: true -->';" in source
    assert "has no explicit ${marker} marker; skip" in source
    assert "has no explicit automerge label; skip" in source
    assert "pr.mergeable === false" in source
    assert "lost explicit automerge marker before merge" in source
    assert "lost automerge label before merge" in source
    assert "finalPr.mergeable === false" in source


def test_merge_on_green_final_refetches_pr_immediately_before_merge() -> None:
    source = _read(MERGE_WORKFLOW)

    final_refetch = source.split("const { data: finalPr } = await github.rest.pulls.get", maxsplit=1)[1]
    pre_merge_block = final_refetch.split("await github.rest.pulls.merge", maxsplit=1)[0]
    assert "pull_number: pr.number" in pre_merge_block
    assert "finalPr.state !== 'open' || finalPr.draft || finalPr.merged" in pre_merge_block
    assert "finalPr.head.sha !== pr.head.sha || finalPr.head.ref !== pr.head.ref" in pre_merge_block
    assert "finalPr.base.sha !== pr.base.sha || finalPr.base.ref !== pr.base.ref" in pre_merge_block
    assert "requireCurrentContext(run, finalPr" in pre_merge_block
    assert "requireCurrentContext(exactRun, finalPr" in pre_merge_block


def test_merge_on_green_merge_call_is_exact_head_squash() -> None:
    source = _read(MERGE_WORKFLOW)

    merge_block = source.split("await github.rest.pulls.merge", maxsplit=1)[1].split(
        "core.notice",
        maxsplit=1,
    )[0]
    assert "pull_number: finalPr.number" in merge_block
    assert "sha: finalPr.head.sha" in merge_block
    assert "merge_method: 'squash'" in merge_block


def test_merge_on_green_remains_the_sole_merger() -> None:
    label_source = _read(LABEL_WORKFLOW)
    merge_source = _read(MERGE_WORKFLOW)

    assert "pulls.merge" not in label_source
    assert merge_source.count("pulls.merge") == 1
    assert "createWorkflowDispatch" in merge_source
    assert "github.rest.actions.reRunWorkflow" not in merge_source


def test_zero_touch_doc_records_token_boundary_and_late_opt_in_contract() -> None:
    doc = _read(ZERO_TOUCH_DOC)

    assert "`<!-- ppe-automerge: true -->`" in doc
    assert "Normal non-draft PRs without the marker remain reviewable and are not labeled" in doc
    assert "`GITHUB_TOKEN`" in doc
    assert "`pull_request:labeled`" in doc
    assert "does not create a new workflow run" in doc
    assert "request a full rerun of the latest successful exact-head `ci.yml`" in doc
    assert "preserved SHA/ref is the original PR merge context" in doc
    assert "Head equality is not enough after the base branch advances" in doc
    assert "current PR number, head SHA, head ref when available, base SHA, and base ref" in doc
    assert "missing association, ambiguous association" in doc
    assert "stale base SHA" in doc
    assert "If an exact-head CI run is already active" in doc
    assert "does not request a duplicate rerun" in doc
    assert "not successful, the label workflow fails visibly and does not rerun it" in doc
    assert "refreshing or rebasing the PR branch is a separate action" in doc
    assert "The label workflow never updates branches" in doc
    assert "The labeling workflow never merges" in doc
    assert "no PAT, GitHub App, or new secret is required" in doc
    assert "Merge on Green also requires that current-context association" in doc
    assert "does not infer a pull request from a branch name" in doc
    assert "stale-base workflow completion cannot merge" in doc
    assert "exact workflow-run ID alone is insufficient" in doc
    assert "refetches the PR immediately before merge" in doc
    assert "guards the merge with the exact final head SHA" in doc
    assert "Merge on Green remains the sole merger" in doc
