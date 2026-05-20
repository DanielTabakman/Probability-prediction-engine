"""
Ensure the Streamlit entrypoint imports when sys.path mirrors production.

Streamlit typically prepends src/viz to sys.path without the repo root, which breaks
`from src.*` unless app.py bootstraps the project root. This test runs in a subprocess
so loading app.py does not pollute the pytest process.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_APP_ENTRY = REPO_ROOT / "src" / "viz" / "app.py"

_ENTRY_CHECK = """
import importlib.util
import sys
from pathlib import Path

repo = Path({repo!r})
viz = repo / "src" / "viz"
app = viz / "app.py"

sys.path = [str(viz)] + [
    p
    for p in sys.path
    if p and Path(p).resolve() != repo.resolve()
]

spec = importlib.util.spec_from_file_location("ppe_app_entry_smoke", app)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load entry spec from {{app}}")

mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if not hasattr(mod, "ROOT"):
    raise AssertionError("app entry missing ROOT after import")

if Path(mod.ROOT).resolve() != repo.resolve():
    raise AssertionError(f"ROOT={{mod.ROOT!r}} does not match repo={{repo!r}}")
""".strip()


def test_app_entrypoint_imports_with_streamlit_sys_path() -> None:
    assert _APP_ENTRY.is_file(), f"missing Streamlit entry: {_APP_ENTRY}"

    result = subprocess.run(
        [sys.executable, "-c", _ENTRY_CHECK.format(repo=str(REPO_ROOT))],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        "app entry import failed with Streamlit-like sys.path\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
