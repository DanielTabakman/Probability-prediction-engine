from __future__ import annotations

from pathlib import Path

from scripts.ppe_delegation_envelope import classify_paths

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
