"""Non-mutating staged Python-to-PowerShell task transport validation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from src.msos_autobuilder.self_update_supervisor import MANAGED_TASK_NAMES

TRANSPORT_MODULE_NAME = "_ppe_staged_self_update_supervisor"


def _probe_script() -> str:
    tasks_literal = repr(MANAGED_TASK_NAMES)
    return textwrap.dedent(
        f"""
        from __future__ import annotations

        import dataclasses
        import importlib.util
        import json
        import sys
        from pathlib import Path

        supervisor_path = Path(sys.argv[1])
        module_name = {TRANSPORT_MODULE_NAME!r}
        task_names = {tasks_literal}
        ready_states = {{name: "Ready" for name in task_names}}

        previous = sys.modules.get(module_name)
        had_previous = module_name in sys.modules
        spec = importlib.util.spec_from_file_location(module_name, supervisor_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to create import spec for {{supervisor_path}}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            if had_previous:
                sys.modules[module_name] = previous
            else:
                sys.modules.pop(module_name, None)

        controller = module.PowerShellTaskController(states=ready_states)
        validation = controller.validate_states(task_names)
        states = dataclasses.asdict(validation)["states"]
        print(
            json.dumps(
                {{
                    "task_names": list(task_names),
                    "validation": dataclasses.asdict(validation),
                    "states_after_probe": ready_states,
                    "sys_modules_restored": sys.modules.get(module_name) is previous
                    if had_previous
                    else module_name not in sys.modules,
                }},
                sort_keys=True,
            )
        )
        """
    ).strip()


def run_staged_task_transport(supervisor_path: Path, *, python_exe: str | None = None) -> dict[str, Any]:
    """Run the exact staged handoff import probe and retain complete process output."""
    proc = subprocess.run(
        [python_exe or sys.executable, "-c", _probe_script(), str(supervisor_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    output = f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    parsed: dict[str, Any] | None = None
    if proc.returncode == 0 and proc.stdout.strip():
        parsed = json.loads(proc.stdout)
    return {
        "validation_results": {
            "passed": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "output": output,
            "parsed": parsed,
        }
    }
