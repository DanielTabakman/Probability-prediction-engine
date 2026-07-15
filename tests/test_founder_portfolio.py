"""Tests for read-only founder portfolio commands."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANON = [
    "docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md",
    "docs/SOP/FOUNDER_PIPELINE_COMMANDS_V1.md",
    "docs/SOP/PIPELINE_CREATION_SOP_V1.md",
    "docs/SOP/SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md",
]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _minimal_repo(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir(parents=True)
    shutil.copyfile(REPO / "config/founder_pipeline_registry.json", tmp_path / "config/founder_pipeline_registry.json")
    for rel in CANON:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# canon\n", encoding="utf-8")
    _write_json(tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json", {"version": 1, "status": "COMPLETE"})
    _write_json(tmp_path / "docs/SOP/PHASE_QUEUE.json", {"version": 1, "items": []})
    _write_json(tmp_path / "docs/SOP/PHASE_CHAPTER_BACKLOG.json", {"version": 1, "items": []})
    return tmp_path


def _write_multislice_ready_repo(
    repo: Path,
    *,
    control_status: str | None = None,
    control_non_blocking: bool = False,
    selection_text: str = "**SELECTED**",
    backlog_status: str | None = None,
    active_manifest_plan: str | None = None,
    active_run_slice: str | None = None,
    operator_text: str | None = None,
) -> Path:
    plan_rel = "docs/SOP/PHASE_PLANS/fixture_relay.json"
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": plan_rel,
                    "status": "READY",
                    "reason": "[HIGH] Fixture",
                }
            ],
        },
    )
    control_slice = {
        "sliceId": "Fixture-Control-Slice001",
        "layerPreset": "CONTROL",
        "declaredPlane": "EVIDENCE-PLANE",
        "buildBranch": "build/auto/control",
    }
    if control_non_blocking:
        control_slice["nonBlocking"] = True
    _write_json(
        repo / plan_rel,
        {
            "name": "fixture",
            "sprintSpecPath": "docs/SOP/SPRINT_FIXTURE.md",
            "selectionRecord": "docs/SOP/POST_FIXTURE_SELECTION.md",
            "slices": [
                control_slice,
                {
                    "sliceId": "Fixture-Product-Slice002",
                    "layerPreset": "PPE_UI",
                    "declaredPlane": "PRODUCT-PLANE",
                    "buildBranch": "build/auto/product",
                    "touchSet": ["src/viz/panel.py"],
                },
                {
                    "sliceId": "Fixture-Closeout-Slice003",
                    "layerPreset": "CONTROL",
                    "declaredPlane": "EVIDENCE-PLANE",
                    "buildBranch": "build/auto/closeout",
                    "closeout": {"evidenceDoc": "docs/SOP/FIXTURE_EVIDENCE_STATUS.md"},
                },
            ],
        },
    )
    (repo / "docs/SOP/SPRINT_FIXTURE.md").write_text("# sprint\n", encoding="utf-8")
    (repo / "docs/SOP/POST_FIXTURE_SELECTION.md").write_text(f"# selection\n\n{selection_text}\n", encoding="utf-8")
    if backlog_status is not None:
        _write_json(
            repo / "docs/SOP/PHASE_CHAPTER_BACKLOG.json",
            {
                "version": 1,
                "items": [
                    {
                        "chapterId": "fixture",
                        "status": backlog_status,
                        "planPath": plan_rel,
                    }
                ],
            },
        )
    if active_manifest_plan is not None:
        _write_json(
            repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
            {"version": 1, "status": "READY", "phasePlanPath": active_manifest_plan},
        )
    if active_run_slice is not None:
        _write_json(
            repo / "artifacts/orchestrator/ACTIVE_RUN.json",
            {
                "version": 1,
                "phasePlanPath": plan_rel,
                "slice_id": active_run_slice,
                "stage": "RUNNING",
            },
        )
    if operator_text is not None:
        path = repo / "artifacts/orchestrator/OPERATOR_STATUS.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(operator_text, encoding="utf-8")
    if control_status is not None:
        (repo / "docs/SOP/FIXTURE_EVIDENCE_STATUS.md").write_text(
            "\n".join(
                [
                    "# Fixture evidence",
                    "",
                    "| Slice | Status | Notes |",
                    "|---|---|---|",
                    f"| Fixture-Control-Slice001 | {control_status} | control witness |",
                    "| Fixture-Product-Slice002 | PENDING | product |",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    return repo


def _fixture_control_status(repo: Path) -> dict:
    from scripts.founder_portfolio import collect_portfolio

    snapshot = collect_portfolio(repo)
    return snapshot["pipelines"][0]["ready_work"][0]["native_prerequisites"]["statuses"]["Fixture-Control-Slice001"]


def _claim_kinds(status: dict) -> set[str]:
    return {claim["kind"] for claim in status["claims"]}


def _hash_tree(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def test_commands_lists_only_founder_vocabulary() -> None:
    from scripts.founder_portfolio import format_commands

    body = format_commands()
    assert "what's next" in body
    assert "what's running" in body
    assert "create pipeline <name>" in body
    assert "build next: Installed one-shot dispatch" in body
    assert "installed/enabled one-shot dispatch" in body
    assert "build next <number>: Fill up to N safe build slots once. Disabled/unimplemented." in body
    assert "keep <number> running: Maintain continuous safe capacity. Disabled/unimplemented." in body
    assert "pause builds: Pause automatic dispatch. Disabled/unimplemented." in body
    assert "resume builds: Refresh state and resume prior capacity. Disabled/unimplemented." in body
    assert "scripts/ppe_" not in body
    assert "never dispatches, enqueues, approves, repairs, or writes" in body


def test_whats_next_is_read_only_for_repo_files(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    before = _hash_tree(repo)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("MSOS_AUTOBUILDER_STATUS_ROOT", None)
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/founder_portfolio.py"), "whats-next", "--json", "--repo-root", str(repo)],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    after = _hash_tree(repo)
    assert proc.returncode == 0, proc.stderr
    assert before == after
    payload = json.loads(proc.stdout)
    assert payload["read_only"] is True


def test_ppe_manifest_running_without_active_run_is_stale(tmp_path: Path) -> None:
    from scripts.founder_portfolio import collect_portfolio

    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
        {"version": 1, "status": "RUNNING", "phasePlanPath": "docs/SOP/PHASE_PLANS/demo_relay.json"},
    )
    snapshot = collect_portfolio(repo)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")
    assert ppe["state"] == "BLOCKED"
    assert any("ACTIVE_RUN.json is missing" in item["message"] for item in ppe["stale_evidence"])
    assert ppe["running_work"] == []


def test_autobuilder_external_source_unavailable_does_not_read_ppe_artifact(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "artifacts/orchestrator/AUTOBUILDER_STATUS.json",
        {
            "version": 1,
            "as_of": "2099-01-01T00:00:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "build": {"slice_id": "must-not-read-from-ppe"},
        },
    )
    snapshot = collect_portfolio(repo)
    autobuilder = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "autobuilder")
    assert autobuilder["state"] == "BLOCKED"
    assert autobuilder["native_state"] == "EXTERNAL_SOURCE_UNAVAILABLE"
    assert autobuilder["running_work"] == []
    assert any("PPE checkout is not a fallback" in item.get("message", "") for item in autobuilder["stale_evidence"])


def test_autobuilder_stale_external_runtime_is_not_counted_running(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    repo = _minimal_repo(tmp_path / "ppe")
    external = tmp_path / "msos-autobuilder"
    _write_json(
        external / "artifacts/orchestrator/AUTOBUILDER_STATUS.json",
        {
            "version": 1,
            "as_of": "2000-01-01T00:00:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "build": {"slice_id": "old-build"},
        },
    )
    monkeypatch.setenv("MSOS_AUTOBUILDER_STATUS_ROOT", str(external))
    snapshot = collect_portfolio(repo)
    autobuilder = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "autobuilder")
    assert autobuilder["state"] == "BLOCKED"
    assert autobuilder["running_work"] == []
    assert any(item["kind"] == "stale" for item in autobuilder["stale_evidence"])


def test_ready_to_build_is_not_reported_as_queued(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/ppe_ready_relay.json",
                    "status": "READY",
                    "reason": "Ready but not dispatched",
                }
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")
    assert [item["state"] for item in ppe["ready_work"]] == ["READY_TO_BUILD"]
    assert ppe["queued_work"] == []
    assert snapshot["capacity"]["ready"] == 1
    assert snapshot["capacity"]["queued"] == 0


def test_selected_multislice_work_contains_deterministic_prerequisite_packet(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status="PENDING")
    first = collect_portfolio(repo)
    second = collect_portfolio(repo)
    work = next(item for item in first["pipelines"][0]["ready_work"] if item["work_item_id"] == "fixture")
    packet = work["native_prerequisites"]

    assert packet["read_only"] is True
    assert packet["source"] == "ppe_native_read_only"
    assert packet["dispatchable"] is False
    assert packet["dispatch_blockers"]
    assert packet["evidence"]["identity"] == next(
        item for item in second["pipelines"][0]["ready_work"] if item["work_item_id"] == "fixture"
    )["native_prerequisites"]["evidence"]["identity"]
    assert packet["statuses"]["Fixture-Control-Slice001"]["status"] == "pending"
    assert packet["statuses"]["Fixture-Control-Slice001"]["non_blocking"] is False
    assert any(
        source["path"] == "docs/SOP/FIXTURE_EVIDENCE_STATUS.md"
        for source in packet["evidence"]["source_files"]
    )
    assert "as_of" not in packet["evidence"]
    assert "generated_at" in packet


def test_queue_state_contributes_explicit_claim(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status="COMPLETE")

    status = _fixture_control_status(repo)

    assert "queue" in _claim_kinds(status)
    assert any(claim["source"] == "docs/SOP/PHASE_QUEUE.json" and claim["state"] == "ready" for claim in status["claims"])


def test_active_manifest_mismatch_blocks_prerequisite(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(
        _minimal_repo(tmp_path),
        control_status="COMPLETE",
        active_manifest_plan="docs/SOP/PHASE_PLANS/other_relay.json",
    )

    status = _fixture_control_status(repo)

    assert status["status"] == "blocked"
    assert "active_manifest" in _claim_kinds(status)
    assert "other_relay.json" in status["evidence"]


def test_selected_and_not_selected_selection_records_affect_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    selected = _write_multislice_ready_repo(_minimal_repo(tmp_path / "selected"), control_status="COMPLETE")
    not_selected = _write_multislice_ready_repo(
        _minimal_repo(tmp_path / "not-selected"),
        control_status="COMPLETE",
        selection_text="**NOT SELECTED** - blocked",
    )

    assert _fixture_control_status(selected)["status"] == "completed"
    blocked = _fixture_control_status(not_selected)
    assert blocked["status"] == "blocked"
    assert "selection record says NOT SELECTED" in blocked["evidence"]


def test_backlog_blocked_or_deferred_state_affects_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    for state in ("blocked", "deferred"):
        repo = _write_multislice_ready_repo(_minimal_repo(tmp_path / state), control_status="COMPLETE", backlog_status=state)

        status = _fixture_control_status(repo)

        assert status["status"] == "blocked"
        assert "backlog" in _claim_kinds(status)
        assert f"backlog status={state}" in status["evidence"]


def test_matching_active_run_affects_prerequisite_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(
        _minimal_repo(tmp_path),
        control_status="COMPLETE",
        active_run_slice="Fixture-Control-Slice001",
    )

    status = _fixture_control_status(repo)

    assert status["status"] == "blocked"
    assert "active_run" in _claim_kinds(status)
    assert "active run stage=RUNNING" in status["evidence"]


def test_operator_status_can_block_prerequisite_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(
        _minimal_repo(tmp_path),
        control_status="COMPLETE",
        operator_text="**Mode:** `CLOSEOUT_ONLY` - fixture product on main; do NOT re-BUILD.",
    )

    status = _fixture_control_status(repo)

    assert status["status"] == "blocked"
    assert "operator_status" in _claim_kinds(status)
    assert "do-not-rebuild" in status["evidence"].lower()


def test_multiple_conflicting_current_claims_are_retained_and_blocked(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status="PENDING", backlog_status="done")

    status = _fixture_control_status(repo)

    assert status["status"] == "blocked"
    assert "conflicting native evidence" in status["evidence"]
    assert "backlog" in _claim_kinds(status)
    assert "evidence_status" in _claim_kinds(status)


def test_duplicate_metric_rows_use_latest_timestamp_not_iteration_order(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status=None)
    rows = [
        {"slice_id": "Fixture-Control-Slice001", "status": "closed", "completed_at": "2030-01-02T00:00:00Z"},
        {"slice_id": "Fixture-Control-Slice001", "status": "failed", "completed_at": "2030-01-01T00:00:00Z"},
    ]
    path = repo / "artifacts/workflow_metrics/slices.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    status = _fixture_control_status(repo)

    assert status["status"] == "completed"
    assert "latest accepted workflow metric status=closed" in status["evidence"]


def test_missing_prerequisite_evidence_remains_pending(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status=None)
    snapshot = collect_portfolio(repo)
    work = snapshot["pipelines"][0]["ready_work"][0]

    status = work["native_prerequisites"]["statuses"]["Fixture-Control-Slice001"]
    assert status["status"] == "pending"
    assert "no accepted PPE native completion" in status["evidence"]


def test_explicit_native_completion_permits_product_slice(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status="COMPLETE")
    snapshot = collect_portfolio(repo)
    status = snapshot["pipelines"][0]["ready_work"][0]["native_prerequisites"]["statuses"][
        "Fixture-Control-Slice001"
    ]
    packet = snapshot["pipelines"][0]["ready_work"][0]["native_prerequisites"]

    assert status["status"] == "completed"
    assert status["non_blocking"] is False
    assert packet["dispatchable"] is True


def test_explicit_non_blocking_evidence_permits_product_slice(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status=None, control_non_blocking=True)
    snapshot = collect_portfolio(repo)
    status = snapshot["pipelines"][0]["ready_work"][0]["native_prerequisites"]["statuses"][
        "Fixture-Control-Slice001"
    ]
    packet = snapshot["pipelines"][0]["ready_work"][0]["native_prerequisites"]

    assert status["status"] == "pending"
    assert status["non_blocking"] is True
    assert packet["dispatchable"] is True


def test_prerequisite_identity_changes_when_evidence_changes(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status="PENDING")
    first = collect_portfolio(repo)["pipelines"][0]["ready_work"][0]["native_prerequisites"]["evidence"]["identity"]
    evidence = repo / "docs/SOP/FIXTURE_EVIDENCE_STATUS.md"
    evidence.write_text(evidence.read_text(encoding="utf-8").replace("PENDING", "COMPLETE"), encoding="utf-8")
    second = collect_portfolio(repo)["pipelines"][0]["ready_work"][0]["native_prerequisites"]["evidence"]["identity"]

    assert first != second


def test_prerequisite_identity_is_deterministic_across_same_commit_worktrees(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo_a = _write_multislice_ready_repo(_minimal_repo(tmp_path / "a"), control_status="PENDING")
    repo_b = _write_multislice_ready_repo(_minimal_repo(tmp_path / "b"), control_status="PENDING")

    identity_a = collect_portfolio(repo_a)["pipelines"][0]["ready_work"][0]["native_prerequisites"]["evidence"][
        "identity"
    ]
    identity_b = collect_portfolio(repo_b)["pipelines"][0]["ready_work"][0]["native_prerequisites"]["evidence"][
        "identity"
    ]

    assert identity_a == identity_b


def test_filesystem_mtime_does_not_change_identity_or_source_evidence_time(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _write_multislice_ready_repo(_minimal_repo(tmp_path), control_status="PENDING")
    first_packet = collect_portfolio(repo)["pipelines"][0]["ready_work"][0]["native_prerequisites"]
    evidence_doc = repo / "docs/SOP/FIXTURE_EVIDENCE_STATUS.md"
    os.utime(evidence_doc, (100, 100))
    second_packet = collect_portfolio(repo)["pipelines"][0]["ready_work"][0]["native_prerequisites"]

    assert first_packet["evidence"]["identity"] == second_packet["evidence"]["identity"]
    assert "as_of" not in first_packet["evidence"]
    assert "as_of" not in second_packet["evidence"]
    assert first_packet["evidence"]["source_files"] == second_packet["evidence"]["source_files"]


def test_current_live_dist_stats_legibility_is_not_ready_after_reconciliation(monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    snapshot = collect_portfolio(REPO)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")

    ready_ids = {item["work_item_id"] for item in ppe["ready_work"]}
    assert "mvp1_distribution_stats_legibility" not in ready_ids
    assert snapshot["recommended_next_action"]["work_item_id"] != "mvp1_distribution_stats_legibility"


def test_current_workflow_persistence_is_not_ready_after_reconciliation(monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    snapshot = collect_portfolio(REPO)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")

    ready_ids = {item["work_item_id"] for item in ppe["ready_work"]}
    assert "msos_workflow_persistence_v1" not in ready_ids
    assert snapshot["recommended_next_action"]["work_item_id"] != "msos_workflow_persistence_v1"


def test_current_snapshot_owner_is_not_ready_after_reconciliation(monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    snapshot = collect_portfolio(REPO)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")

    ready_ids = {item["work_item_id"] for item in ppe["ready_work"]}
    assert "mvp1_snapshot_owner_v1" not in ready_ids
    assert snapshot["recommended_next_action"]["work_item_id"] != "mvp1_snapshot_owner_v1"


def test_issue_5374_reconciled_items_do_not_reappear_after_uso_witness_selection(monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    snapshot = collect_portfolio(REPO)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")

    reconciled_ids = {
        "repo_housekeeping_v1",
        "msos_strategy_lab_distribution_demo",
        "msos_storyboard_visual_parity_v1",
        "msos_access_identity_v1",
        "msos_monitor_history_live_v1",
        "msos_entitlements_v1",
        "msos_strategy_lab_embed_shell_v1",
        "msos_billing_stripe_v1",
        "ppe_tradeable_universe_v1",
        "mvp1_cross_venue_scan_v1",
        "msos_forward_consistency_radar_v1",
        "ppe_hyperliquid_perp_rail_v1",
        "repo_between_chapter_housekeeping",
    }
    ready_ids = {item["work_item_id"] for item in ppe["ready_work"]}

    assert ready_ids == {"ppe_commodity_proxy_tier1_v1"}
    assert ready_ids.isdisjoint(reconciled_ids)
    assert snapshot["recommended_next_action"]["work_item_id"] not in reconciled_ids


def test_blocked_autobuilder_does_not_prevent_safe_ppe_recommendation(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/ppe_safe_relay.json",
                    "status": "READY",
                    "reason": "Safe PPE work",
                    "priority": "medium",
                }
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    assert snapshot["recommended_next_action"]["pipeline_id"] == "ppe"
    assert snapshot["recommended_next_action"]["state"] == "READY_TO_BUILD"


def test_manual_frontier_files_are_not_native_runtime(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    snapshot = collect_portfolio(repo)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")
    manifest_evidence = next(item for item in ppe["evidence"] if item["source"] == "docs/SOP/ACTIVE_PHASE_MANIFEST.json")
    assert manifest_evidence["kind"] == "manual"


def test_deterministic_selection_uses_priority_then_tie_break(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/z_medium_relay.json",
                    "status": "READY",
                    "reason": "Medium work",
                    "priority": "medium",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/a_high_relay.json",
                    "status": "READY",
                    "reason": "High work",
                    "priority": "high",
                },
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    rec = snapshot["recommended_next_action"]
    assert rec["work_item_id"] == "a_high"
    assert "selection_explanation" in rec

    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/z_equal_relay.json",
                    "status": "READY",
                    "reason": "Equal Z",
                    "priority": "high",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/a_equal_relay.json",
                    "status": "READY",
                    "reason": "Equal A",
                    "priority": "high",
                },
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    # Age within the same priority class wins before deterministic ID tie-break.
    assert snapshot["recommended_next_action"]["work_item_id"] == "z_equal"


def test_deterministic_tie_breaker_is_stable() -> None:
    from scripts.founder_portfolio import _recommend_next

    base_selection = {
        "founder_priority_rank": 1,
        "deadline_rank": "9999-12-31T00:00:00+00:00",
        "dependency_unblock_value": 0,
        "age_index": 0,
    }
    snapshot = [
        {
            "pipeline_id": "zpipe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                {
                    "work_item_id": "work",
                    "title": "Z work",
                    "evidence": "manual",
                    "selection": base_selection,
                }
            ],
        },
        {
            "pipeline_id": "apipe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                {
                    "work_item_id": "work",
                    "title": "A work",
                    "evidence": "manual",
                    "selection": base_selection,
                }
            ],
        },
    ]
    assert _recommend_next(snapshot)["pipeline_id"] == "apipe"


def test_selection_deadline_and_dependency_unblock_order() -> None:
    from scripts.founder_portfolio import _recommend_next

    def work(work_item_id: str, *, deadline: str, unblock: int) -> dict:
        return {
            "work_item_id": work_item_id,
            "title": work_item_id,
            "evidence": "manual",
            "selection": {
                "founder_priority_rank": 1,
                "deadline_rank": deadline,
                "dependency_unblock_value": unblock,
                "age_index": 0,
            },
        }

    deadline_snapshot = [
        {
            "pipeline_id": "ppe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                work("later", deadline="2030-01-02T00:00:00+00:00", unblock=99),
                work("earlier", deadline="2030-01-01T00:00:00+00:00", unblock=1),
            ],
        }
    ]
    assert _recommend_next(deadline_snapshot)["work_item_id"] == "earlier"

    unblock_snapshot = [
        {
            "pipeline_id": "ppe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                work("low-unblock", deadline="2030-01-01T00:00:00+00:00", unblock=1),
                work("high-unblock", deadline="2030-01-01T00:00:00+00:00", unblock=5),
            ],
        }
    ]
    assert _recommend_next(unblock_snapshot)["work_item_id"] == "high-unblock"


def test_selection_fairness_prefers_pipeline_without_active_work() -> None:
    from scripts.founder_portfolio import _recommend_next

    selection = {
        "founder_priority_rank": 1,
        "deadline_rank": "9999-12-31T00:00:00+00:00",
        "dependency_unblock_value": 0,
        "age_index": 0,
    }
    snapshot = [
        {
            "pipeline_id": "busy",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [{"work_item_id": "already-running"}],
            "queued_work": [],
            "ready_work": [{"work_item_id": "busy-next", "title": "busy", "evidence": "manual", "selection": selection}],
        },
        {
            "pipeline_id": "idle",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [{"work_item_id": "idle-next", "title": "idle", "evidence": "manual", "selection": selection}],
        },
    ]
    assert _recommend_next(snapshot)["pipeline_id"] == "idle"


def test_unsupported_build_next_does_not_dispatch() -> None:
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/founder_portfolio.py"), "build", "next"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 2
    assert "unsupported or non-read-only command" in proc.stderr
