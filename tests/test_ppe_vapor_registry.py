"""Tests for product vapor registry."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_discover_finds_planned_module_classes() -> None:
    from scripts.ppe_vapor_registry import discover_items

    items = discover_items(REPO)
    ids = {i["id"] for i in items}
    assert "module_class_positioning" in ids or "module_class_replay" in ids


def test_discover_finds_interaction_modes() -> None:
    from scripts.ppe_vapor_registry import discover_items

    items = discover_items(REPO)
    assert any(i.get("kind") == "vision" for i in items)
    assert any("Interaction mode" in str(i.get("title") or "") for i in items)


def test_discover_ui_fixtures_when_files_present() -> None:
    from scripts.ppe_vapor_registry import discover_items

    items = discover_items(REPO)
    ids = {i["id"] for i in items}
    assert "ui_fixture_forward_consistency" in ids


def test_sync_writes_json_and_markdown(tmp_path: Path) -> None:
    from scripts.ppe_vapor_registry import REGISTRY_MD_REL, REGISTRY_REL, sync_registry

    repo = tmp_path
    (repo / "docs" / "SOP").mkdir(parents=True)
    (repo / "docs" / "VISION" / "MSOS").mkdir(parents=True)
    (repo / "apps" / "msos-web" / "src" / "lib").mkdir(parents=True)
    (repo / "apps" / "msos-web" / "src" / "components").mkdir(parents=True)

    for rel in (
        "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
        "docs/SOP/PHASE_QUEUE.json",
        "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
        "apps/msos-web/src/lib/forwardConsistency.ts",
        "apps/msos-web/src/components/StrategyLabClientShell.tsx",
        "docs/SOP/PRODUCT_VAPOR_REGISTRY.json",
    ):
        src = REPO / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    data = sync_registry(repo)
    assert (repo / REGISTRY_REL).is_file()
    assert (repo / REGISTRY_MD_REL).is_file()
    assert isinstance(data.get("items"), list)
    assert data.get("open_count", 0) >= 1


def test_manual_pin_persists_across_sync(tmp_path: Path) -> None:
    from scripts.ppe_vapor_registry import load_registry, open_items, sync_registry

    repo = tmp_path
    (repo / "docs" / "SOP").mkdir(parents=True)
    (repo / "docs" / "VISION" / "MSOS").mkdir(parents=True)
    (repo / "apps" / "msos-web" / "src" / "lib").mkdir(parents=True)
    (repo / "apps" / "msos-web" / "src" / "components").mkdir(parents=True)

    for rel in (
        "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
        "docs/SOP/PHASE_QUEUE.json",
        "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
        "apps/msos-web/src/lib/forwardConsistency.ts",
        "apps/msos-web/src/components/StrategyLabClientShell.tsx",
    ):
        src = REPO / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    reg_path = repo / "docs/SOP/PRODUCT_VAPOR_REGISTRY.json"
    reg_path.write_text(
        json.dumps(
            {
                "version": 1,
                "manual": [
                    {
                        "id": "manual_test_pin",
                        "title": "Pinned vapor idea",
                        "why": "Steward note for later SELECTION",
                        "status": "open",
                    }
                ],
                "items": [],
                "closed_items": [],
            }
        ),
        encoding="utf-8",
    )

    sync_registry(repo)
    reg = load_registry(repo)
    manual_ids = {str(m.get("id") or "") for m in reg.get("manual") or []}
    assert "manual_test_pin" in manual_ids

    open_ids = {i["id"] for i in open_items(repo)}
    assert "manual_test_pin" in open_ids


def test_module_excluded_when_queue_active(tmp_path: Path) -> None:
    from scripts.ppe_vapor_registry import discover_items

    repo = tmp_path
    (repo / "docs" / "SOP").mkdir(parents=True)
    (repo / "docs" / "VISION" / "MSOS").mkdir(parents=True)

    (repo / "docs/SOP/PPE_MODULE_REGISTRY_V1.md").write_text(
        (REPO / "docs/SOP/PPE_MODULE_REGISTRY_V1.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (repo / "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md").write_text(
        (REPO / "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    queue = json.loads((REPO / "docs/SOP/PHASE_QUEUE.json").read_text(encoding="utf-8"))
    for item in queue.get("items") or []:
        if "forward_consistency" in str(item.get("planPath") or "").lower():
            item["status"] = "READY"
    (repo / "docs/SOP/PHASE_QUEUE.json").write_text(json.dumps(queue), encoding="utf-8")

    items = discover_items(repo)
    ids = {i["id"] for i in items}
    assert "module_forward_consistency" not in ids
