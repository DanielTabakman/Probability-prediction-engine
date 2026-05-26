"""Tests for scripts/ppe_git_network.py."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.ppe_git_network import (
    git_network_mode,
    local_git_only_enabled,
    try_git_push,
)


def test_local_git_only_env():
    with patch.dict(os.environ, {"PPE_LOCAL_GIT_ONLY": "1"}, clear=False):
        assert local_git_only_enabled() is True
        assert git_network_mode() == "local_only"


def test_try_git_push_skipped_when_local_only(tmp_path: Path):
    with patch.dict(os.environ, {"PPE_LOCAL_GIT_ONLY": "1"}, clear=False):
        result = try_git_push(tmp_path)
    assert result["ok"] is True
    assert result["skipped"] is True


def test_try_git_push_runs_when_normal(tmp_path: Path):
    proc = MagicMock()
    proc.returncode = 0
    proc.stdout = ""
    proc.stderr = ""

    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("PPE_LOCAL_GIT_ONLY", None)
        with patch("scripts.ppe_git_network.subprocess.run", return_value=proc) as run:
            result = try_git_push(tmp_path)
    assert result["ok"] is True
    assert result["skipped"] is False
    run.assert_called_once()
