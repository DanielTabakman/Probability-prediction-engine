"""Tests for operator compass auto-sync."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_build_compass_includes_verdict_do_now() -> None:
    from scripts.ppe_operator_compass import build_compass

    status = {
        "as_of": "2026-06-29T20:00:00Z",
        "verdict": "RUN_LOCAL",
        "chapter_name": "PPE_exposure_menu_v1",
        "blocker": "IDE product marker present",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/ppe_exposure_menu_v1_relay.json",
        "supply": {"queue_ready": 1},
    }
    compass = build_compass(REPO, status=status)
    ids = [item["id"] for item in compass["do_now"]]
    assert "verdict_run_local" in ids
    assert any("exposure" in item["title"].lower() or "closeout" in item["title"].lower() for item in compass["do_now"])
    assert compass["relay_busy"] is True
    assert not any(item["id"].startswith("program_") for item in compass["do_now"])


def test_program_queue_hidden_from_do_now_when_relay_busy() -> None:
    from scripts.ppe_operator_compass import build_compass

    busy = build_compass(REPO, status={"as_of": "2026-06-29T20:00:00Z", "verdict": "RUN_LOCAL", "chapter_name": "msos_strategy_lab_dist_download_v1"})
    assert busy["relay_busy"] is True
    assert not any(i["id"].startswith("program_") for i in busy["do_now"])

    idle = build_compass(REPO, status={"as_of": "2026-06-29T20:00:00Z", "verdict": "SUPPLY_LOW", "supply": {"queue_ready": 0}})
    assert idle["relay_busy"] is False
    assert any(i["id"].startswith("program_") for i in idle["do_now"])


def test_done_vm_collector_not_in_do_now() -> None:
    from scripts.ppe_operator_compass import build_compass

    status = {"as_of": "2026-06-29T20:00:00Z", "verdict": "RUN_AUTO", "supply": {"queue_ready": 1}}
    compass = build_compass(REPO, status=status)
    text = json.dumps(compass["do_now"]).lower()
    assert "cross_venue_collector_vm_install" not in text
    assert "install_horizon_surface_collector" not in text


def test_parse_module_registry_from_markdown() -> None:
    from scripts.ppe_operator_compass import _parse_module_registry

    modules = _parse_module_registry(REPO)
    assert len(modules) >= 6
    ids = {m["module_id"] for m in modules}
    assert "implied_distribution" in ids
    assert "exposure_menu" in ids
    assert all(m.get("status") for m in modules)


def test_sync_compass_writes_json_and_patches_map(tmp_path: Path) -> None:
    from scripts.ppe_operator_compass import COMPASS_REL, MAP_REL, sync_compass

    repo = tmp_path
    (repo / "docs" / "SOP" / "assets").mkdir(parents=True)
    (repo / "artifacts" / "control_plane").mkdir(parents=True)
    src_map = REPO / MAP_REL
    (repo / MAP_REL).write_text(src_map.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "docs" / "SOP" / "PPE_MODULE_REGISTRY_V1.md").write_text(
        (REPO / "docs/SOP/PPE_MODULE_REGISTRY_V1.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in ("config/operator_program_queue.yaml", "config/assets_tier1_manifest.yaml", "docs/SOP/PHASE_QUEUE.json"):
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text((REPO / rel).read_text(encoding="utf-8"), encoding="utf-8")

    status = {
        "as_of": "2026-06-29T20:00:00Z",
        "verdict": "RUN_LOCAL",
        "chapter_name": "test_chapter",
        "blocker": "test blocker",
        "phase_plan_path": "",
        "supply": {"queue_ready": 0},
    }
    sync_compass(repo, status=status, patch_map=True)

    compass_path = repo / COMPASS_REL
    assert compass_path.is_file()
    compass = json.loads(compass_path.read_text(encoding="utf-8"))
    assert compass["do_now"]

    html = (repo / MAP_REL).read_text(encoding="utf-8")
    assert 'id="map-do-now"' in html
    assert 'id="map-program-queue"' in html
    assert "test_chapter" in html or "closeout" in html.lower()
    assert "asset batch —" not in html.lower()
    assert "compass-src" in html
    assert "EDT" in html or "EST" in html


def test_module_map_has_compass_sections() -> None:
    html = (REPO / "docs/SOP/assets/msos_module_map.html").read_text(encoding="utf-8")
    for marker in (
        'id="map-do-now"',
        'id="map-program-queue"',
        'id="map-crack-catcher"',
        'id="map-module-progress"',
        'id="map-waiting-on-time"',
    ):
        assert marker in html, f"missing {marker}"


def test_phone_snippet_lines_from_compass() -> None:
    from scripts.ppe_operator_compass import phone_snippet_lines

    compass = {
        "do_now": [{"title": "Finish closeout", "why": "RUN_LOCAL on desktop"}],
        "crack_catcher": [{"title": "Horizon replay", "why": "8 / 30 snapshots"}],
        "sources": {"operator_verdict": "RUN_LOCAL"},
    }
    lines = phone_snippet_lines(REPO, compass=compass)
    assert lines[0] == "Your compass (module map)"
    assert any(line.startswith("- Do now:") for line in lines)
    assert any(line.startswith("- Watch:") for line in lines)


def test_write_notify_snippet_creates_json(tmp_path: Path) -> None:
    from scripts.ppe_operator_compass import write_notify_snippet

    compass = {
        "as_of_utc": "2026-06-29T20:00:00Z",
        "do_now": [{"title": "Test action", "why": "because"}],
        "crack_catcher": [],
    }
    path = write_notify_snippet(tmp_path, compass=compass)
    assert path is not None
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["do_now_count"] == 1
    assert "Your compass" in payload["phone_lines"][0]
