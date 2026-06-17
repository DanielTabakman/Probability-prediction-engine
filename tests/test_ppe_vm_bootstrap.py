"""Tests for VM loop-host bootstrap."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_vm_bootstrap import (
    _evidence_has_pending_slices,
    _witness_touchset_only_evidence,
    ensure_loop_host_config,
    sync_slice_progress,
)


def test_ensure_loop_host_config_creates_from_example(tmp_path):
    example = tmp_path / "ppe_operator_loop_host.local.cmd.example"
    example.write_text('@echo off\nset "PPE_LOOP_HOST=1"\n', encoding="utf-8")
    out = ensure_loop_host_config(tmp_path)
    assert out["ok"] is True
    assert out.get("created") is True
    assert (tmp_path / "ppe_operator_loop_host.local.cmd").is_file()


def test_evidence_pending_detection():
    assert _evidence_has_pending_slices("| MSOS-X | PENDING | note |")
    assert not _evidence_has_pending_slices("| MSOS-X | DONE | note |")


def test_witness_touchset_only_evidence():
    assert _witness_touchset_only_evidence(
        {"touchSet": ["docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md"]}
    )
    assert not _witness_touchset_only_evidence({"touchSet": ["docker-compose.yml"]})


def test_sync_skips_closeout_and_pending_witness(tmp_path):
    plan_path = "docs/SOP/PHASE_PLANS/msos_production_wiring_v1_relay.json"
    plan_dir = tmp_path / "docs/SOP/PHASE_PLANS"
    plan_dir.mkdir(parents=True)
    plan_file = plan_dir / "msos_production_wiring_v1_relay.json"
    evidence = tmp_path / "docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        "# evidence\n\n| Slice | Status |\n|-------|--------|\n| X | PENDING |\n",
        encoding="utf-8",
    )
    selection = tmp_path / "docs/SOP/POST_MSOS_PRODUCTION_WIRING_V1_SELECTION.md"
    selection.write_text("SELECTED", encoding="utf-8")
    plan_file.write_text(
        json.dumps(
            {
                "selectionRecord": "docs/SOP/POST_MSOS_PRODUCTION_WIRING_V1_SELECTION.md",
                "slices": [
                    {"sliceId": "MSOS-ProdWireV1-Control-Slice001"},
                    {
                        "sliceId": "MSOS-ProdWireV1-Product-Slice002",
                        "touchSet": ["apps/msos-web/src/lib/msosPublicUrls.ts"],
                    },
                    {
                        "sliceId": "MSOS-ProdWireV1-Witness-Slice004",
                        "touchSet": ["docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md"],
                    },
                    {
                        "sliceId": "MSOS-ProdWireV1-Closeout-Slice005",
                        "closeout": {"chapterId": "msos_production_wiring_v1"},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    touch = tmp_path / "apps/msos-web/src/lib/msosPublicUrls.ts"
    touch.parent.mkdir(parents=True, exist_ok=True)
    touch.write_text("export const x = 1;\n", encoding="utf-8")

    manifest = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest.write_text(json.dumps({"phasePlanPath": plan_path}), encoding="utf-8")

    with patch("scripts.ppe_manifest.load_phase_plan") as load_plan:
        load_plan.return_value = json.loads(plan_file.read_text(encoding="utf-8"))
        out = sync_slice_progress(tmp_path, plan_path)

    marked = set(out.get("marked") or [])
    assert "MSOS-ProdWireV1-Control-Slice001" in marked
    assert "MSOS-ProdWireV1-Product-Slice002" in marked
    assert "MSOS-ProdWireV1-Witness-Slice004" not in marked
    assert "MSOS-ProdWireV1-Closeout-Slice005" not in marked
