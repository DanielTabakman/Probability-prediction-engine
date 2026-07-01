from __future__ import annotations

from pathlib import Path

from scripts.ppe_delegation_envelope import (
    DelegationVerdict,
    classify_paths,
    record_auto_notify,
)

_REPO = Path(__file__).resolve().parents[1]


def test_control_plane_hygiene_is_auto() -> None:
    verdict = classify_paths(
        _REPO,
        ["docs/SOP/PHASE_QUEUE.json", "docs/SOP/TRIGGERED_IDEAS.json"],
    )
    assert verdict.tier == "auto"
    assert verdict.can_auto_ship()


def test_secrets_human_only() -> None:
    verdict = classify_paths(_REPO, [".env", "src/viz/app.py"])
    assert verdict.tier == "human_only"
    assert not verdict.can_auto_ship()


def test_mixed_plane_escalates() -> None:
    verdict = classify_paths(
        _REPO,
        ["docs/SOP/PHASE_QUEUE.json", "src/viz/foo.py"],
        pass_type="BUILD",
    )
    assert verdict.tier == "steward_packet"


def test_recovery_skips_mixed_plane_escalator() -> None:
    verdict = classify_paths(
        _REPO,
        ["docs/SOP/PHASE_QUEUE.json", "src/viz/foo.py"],
        pass_type="RECOVERY",
    )
    assert verdict.tier == "auto"


def test_evidence_suffix_auto() -> None:
    verdict = classify_paths(
        _REPO,
        ["docs/SOP/PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md"],
    )
    assert verdict.tier == "auto"


def test_product_direction_sync_fields_auto(tmp_path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    env_dir = tmp_path / "docs" / "SOP"
    env_dir.mkdir(parents=True)
    (env_dir / "DELEGATION_ENVELOPE_V1.json").write_text(
        (_REPO / "docs/SOP/DELEGATION_ENVELOPE_V1.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    path = env_dir / "ACTIVE_PRODUCT_DIRECTION.json"
    path.write_text(
        '{"pivotId":"a","northStar":"n","primaryFocus":"f","nextStewardAction":"old"}',
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    path.write_text(
        '{"pivotId":"a","northStar":"n","primaryFocus":"f","nextStewardAction":"new"}',
        encoding="utf-8",
    )
    verdict = classify_paths(tmp_path, ["docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"])
    assert verdict.tier == "auto"


def test_product_direction_pivot_field_human_only(tmp_path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    env_dir = tmp_path / "docs" / "SOP"
    env_dir.mkdir(parents=True)
    (env_dir / "DELEGATION_ENVELOPE_V1.json").write_text(
        (_REPO / "docs/SOP/DELEGATION_ENVELOPE_V1.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    path = env_dir / "ACTIVE_PRODUCT_DIRECTION.json"
    path.write_text('{"pivotId":"old","northStar":"n","primaryFocus":"f"}', encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    path.write_text('{"pivotId":"new","northStar":"n","primaryFocus":"f"}', encoding="utf-8")
    verdict = classify_paths(tmp_path, ["docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"])
    assert verdict.tier == "human_only"


def test_record_auto_notify_appends_log(tmp_path: Path) -> None:
    verdict = DelegationVerdict(tier="auto_notify", reasons=["escalator large_diff"])
    out = record_auto_notify(tmp_path, verdict, ["docs/SOP/PHASE_QUEUE.json"], branch="test")
    assert out is not None
    assert out.is_file()
