"""Tests for operator notify secret bootstrap."""

from __future__ import annotations

from pathlib import Path

from scripts.bootstrap_operator_notify_secret import PLACEHOLDER_SECRET, bootstrap_notify_cmd


def test_bootstrap_creates_file_with_secret(tmp_path: Path) -> None:
    example = tmp_path / "ppe_operator_notify.local.cmd.example"
    example.write_text(
        'set "PPE_NTFY_TOPIC=ppe-test-topic"\n'
        f'set "PPE_NTFY_CMD_SECRET={PLACEHOLDER_SECRET}"\n',
        encoding="utf-8",
    )
    target = tmp_path / "ppe_operator_notify.local.cmd"
    result = bootstrap_notify_cmd(tmp_path)
    assert target.is_file()
    assert result["created"] == "True"
    assert result["secret_rotated"] == "True"
    text = target.read_text(encoding="utf-8")
    assert PLACEHOLDER_SECRET not in text
    assert "PPE_NTFY_CMD_SECRET=" in text


def test_bootstrap_preserves_existing_secret(tmp_path: Path) -> None:
    example = tmp_path / "ppe_operator_notify.local.cmd.example"
    example.write_text(
        'set "PPE_NTFY_TOPIC=ppe-test-topic"\n'
        f'set "PPE_NTFY_CMD_SECRET={PLACEHOLDER_SECRET}"\n',
        encoding="utf-8",
    )
    target = tmp_path / "ppe_operator_notify.local.cmd"
    target.write_text(
        'set "PPE_NTFY_TOPIC=ppe-test-topic"\nset "PPE_NTFY_CMD_SECRET=already-set-secret-value"\n',
        encoding="utf-8",
    )
    result = bootstrap_notify_cmd(tmp_path)
    assert result["secret_rotated"] == "False"
    assert "already-set-secret-value" in target.read_text(encoding="utf-8")
