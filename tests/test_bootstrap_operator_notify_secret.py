"""Tests for bootstrap_operator_notify_secret."""

from __future__ import annotations

from pathlib import Path

from scripts.bootstrap_operator_notify_secret import PLACEHOLDER_TOPIC, bootstrap_notify_cmd


def test_bootstrap_creates_notify_file_from_example(tmp_path: Path) -> None:
    example = tmp_path / "ppe_operator_notify.local.cmd.example"
    example.write_text(f'set "PPE_NTFY_TOPIC={PLACEHOLDER_TOPIC}"\n', encoding="utf-8")
    result = bootstrap_notify_cmd(tmp_path)
    target = tmp_path / "ppe_operator_notify.local.cmd"
    assert target.is_file()
    assert result["created"] == "True"
    assert "PPE_NTFY_CMD_SECRET" not in target.read_text(encoding="utf-8")


def test_bootstrap_existing_file_unchanged(tmp_path: Path) -> None:
    target = tmp_path / "ppe_operator_notify.local.cmd"
    example = tmp_path / "ppe_operator_notify.local.cmd.example"
    example.write_text(f'set "PPE_NTFY_TOPIC={PLACEHOLDER_TOPIC}"\n', encoding="utf-8")
    target.write_text('set "PPE_NTFY_TOPIC=ppe-test-topic"\n', encoding="utf-8")
    result = bootstrap_notify_cmd(tmp_path)
    assert result["created"] == "False"
    assert result["topic_placeholder"] == "False"
