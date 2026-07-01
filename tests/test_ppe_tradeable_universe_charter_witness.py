"""Charter witness for PPE tradeable universe program v1."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"
CONFIG = REPO / "config"

PROGRAM = SOP / "PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md"
ADR = SOP / "PPE_TRADEABLE_UNIVERSE_ADR.md"
MANIFEST = CONFIG / "assets_tier1_manifest.yaml"
UNIVERSE_PLAN = SOP / "PHASE_PLANS" / "ppe_tradeable_universe_v1_relay.json"
UNIVERSE_SELECTION = SOP / "POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md"
UNIVERSE_SPRINT = SOP / "SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md"
UNIVERSE_EVIDENCE = SOP / "PPE_TRADEABLE_UNIVERSE_V1_EVIDENCE_STATUS.md"

BATCH_CHAPTERS = (
    "ppe_deribit_crypto_tier1_v1",
    "ppe_equity_universe_tier1a_v1",
    "ppe_equity_universe_tier1b_v1",
    "ppe_equity_universe_tier1c_v1",
    "ppe_commodity_proxy_tier1_v1",
)


def test_tradeable_universe_program_artifacts_exist() -> None:
    for path in (PROGRAM, ADR, MANIFEST, UNIVERSE_PLAN, UNIVERSE_SELECTION, UNIVERSE_SPRINT, UNIVERSE_EVIDENCE):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_universe_phase_plan_valid() -> None:
    plan = json.loads(UNIVERSE_PLAN.read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    assert plan["slices"][0]["sliceId"] == "PPE-Universe-Control-Slice001"
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("chapterId") == "ppe_tradeable_universe_v1"


def test_tier1_manifest_covers_major_groups() -> None:
    body = MANIFEST.read_text(encoding="utf-8")
    for token in ("SOL", "SPY", "AAPL", "GLD", "catalog:", "asset_templates:"):
        assert token in body


def test_batch_chapter_plans_exist_and_validate() -> None:
    for chapter_id in BATCH_CHAPTERS:
        plan_path = SOP / "PHASE_PLANS" / f"{chapter_id}_relay.json"
        selection_path = SOP / f"POST_{chapter_id.upper()}_SELECTION.md"
        assert plan_path.is_file(), chapter_id
        assert selection_path.is_file(), chapter_id
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        assert not validate_phase_plan(plan)


def test_roadmap_lists_universe_program_after_equity() -> None:
    roadmap = json.loads((SOP / "PHASE_SELECTION_ROADMAP.json").read_text(encoding="utf-8"))
    paths = [item["planPath"] for item in roadmap["items"]]
    equity_idx = paths.index("docs/SOP/PHASE_PLANS/ppe_equity_options_v1_relay.json")
    universe_idx = paths.index("docs/SOP/PHASE_PLANS/ppe_tradeable_universe_v1_relay.json")
    assert universe_idx > equity_idx


def test_manifest_points_at_tradeable_universe_chapter() -> None:
    manifest = json.loads((SOP / "ACTIVE_PHASE_MANIFEST.json").read_text(encoding="utf-8"))
    plan = manifest.get("phasePlanPath")
    universe_plan = "docs/SOP/PHASE_PLANS/ppe_tradeable_universe_v1_relay.json"
    if plan == universe_plan:
        assert manifest.get("status") in ("READY", "RUNNING", "COMPLETE")
        return
    queue = json.loads((SOP / "PHASE_QUEUE.json").read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item.get("planPath") == universe_plan)
    assert row["status"] in ("DONE", "READY")


def test_universe_control_slice_closed_in_evidence_doc() -> None:
    body = UNIVERSE_EVIDENCE.read_text(encoding="utf-8")
    row = body.split("PPE-Universe-Control-Slice001", 1)[1].split("\n", 1)[0]
    assert "**CLOSED**" in row
