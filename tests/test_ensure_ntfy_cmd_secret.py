"""Tests for ensure_ntfy_cmd_secret (deprecated no-op)."""

from __future__ import annotations

from pathlib import Path

from scripts.ensure_ntfy_cmd_secret import ensure_secret


def test_ensure_secret_is_noop(tmp_path: Path) -> None:
    path = tmp_path / "ppe_operator_notify.local.cmd"
    path.write_text('set "PPE_NTFY_TOPIC=t"\n', encoding="utf-8")
    result = ensure_secret(tmp_path)
    assert result["action"] == "deprecated_noop"
    assert "PPE_NTFY_CMD_SECRET" not in path.read_text(encoding="utf-8")
