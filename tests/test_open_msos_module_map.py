"""Tests for open_msos_module_map."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.open_msos_module_map import main, open_path


def test_open_path_uses_startfile_on_windows(tmp_path: Path) -> None:
    html = tmp_path / "map.html"
    html.write_text("<html></html>", encoding="utf-8")
    with patch("scripts.open_msos_module_map.sys.platform", "win32"), patch(
        "scripts.open_msos_module_map.os.startfile"
    ) as startfile:
        open_path(html)
        startfile.assert_called_once_with(html.resolve())


def test_main_refreshes_and_opens() -> None:
    repo = Path(__file__).resolve().parents[1]
    with patch("scripts.open_msos_module_map.open_path") as open_path:
        code = main(["--repo-root", str(repo)])
    assert code == 0
    open_path.assert_called_once()
