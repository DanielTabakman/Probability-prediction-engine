from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from src.msos_autobuilder.self_update_supervisor import MANAGED_TASK_NAMES
from src.msos_autobuilder.staged_task_transport import run_staged_task_transport


pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows subprocess regression")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_old_dynamic_import_fails_for_real_dataclass_supervisor() -> None:
    supervisor = _repo_root() / "src" / "msos_autobuilder" / "self_update_supervisor.py"
    script = textwrap.dedent(
        """
        import importlib.util
        import sys
        from pathlib import Path

        supervisor_path = Path(sys.argv[1])
        spec = importlib.util.spec_from_file_location("_ppe_old_staged_supervisor", supervisor_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("missing spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        """
    )

    proc = subprocess.run(
        [sys.executable, "-c", script, str(supervisor)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode != 0
    assert "dataclasses.py" in proc.stderr
    assert "AttributeError" in proc.stderr
    assert "Traceback (most recent call last):" in proc.stderr


def test_repaired_staged_transport_imports_real_supervisor_and_preserves_output() -> None:
    supervisor = _repo_root() / "src" / "msos_autobuilder" / "self_update_supervisor.py"

    report = run_staged_task_transport(supervisor)
    validation_results = report["validation_results"]

    assert validation_results["passed"] is True
    assert validation_results["stderr"] == ""
    assert validation_results["stdout"].strip()
    assert validation_results["output"].startswith("STDOUT:\n")
    parsed = validation_results["parsed"]
    assert parsed["task_names"] == list(MANAGED_TASK_NAMES)
    assert [state["name"] for state in parsed["validation"]["states"]] == list(MANAGED_TASK_NAMES)
    assert parsed["validation"]["task_count"] == 5
    assert parsed["validation"]["ready_count"] == 5
    assert parsed["states_after_probe"] == {name: "Ready" for name in MANAGED_TASK_NAMES}
    assert parsed["sys_modules_restored"] is True
