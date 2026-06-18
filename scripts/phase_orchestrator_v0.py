"""Phase Orchestrator v0 - spawn worker agents, enforce time budgets, gate via relay.

This is intentionally small and mechanical:
- The relay (`scripts/relay_runtime_v0.py`) is the hard gate (preflight, schema, decision policy).
- This orchestrator spawns Cursor CLI workers and loops `resume` until terminal.
- Time budgets:
  - 15 minutes: "sus" threshold (surface for investigation)
  - 30 minutes: hard cap (terminate worker, stop)

The orchestrator is designed to be resumable via its own state file under artifacts/.

Usage (single slice):
  python scripts/phase_orchestrator_v0.py run-slice ^
    --slice-id Sprint004-SliceXXX ^
    --sprint-spec-path artifacts/phase_runs/demo/slices/slice_001.md ^
    --declared-plane PRODUCT-PLANE ^
    --baseline-branch main ^
    --build-branch build/auto/sprint004-slicexxx ^
    --worker-mode cursor-agent

Phase mode is a thin loop over a generated plan file (see `init-phase`).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


REPO_ROOT_SENTINEL = "pyproject.toml"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root(start: Path) -> Optional[Path]:
    cur = start.resolve()
    for _ in range(12):
        if (cur / ".git").exists() and (cur / REPO_ROOT_SENTINEL).exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _run(cmd: list[str], cwd: Path, timeout_s: Optional[int] = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        check=False,
    )
    return int(proc.returncode), (proc.stdout or ""), (proc.stderr or "")


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")


@dataclass(frozen=True)
class SliceRun:
    slice_id: str
    sprint_spec_path: str
    declared_plane: str
    baseline_branch: str
    build_branch: str
    retry_budget_max: int = 2
    repo_layer: dict[str, Any] | None = None


@dataclass(frozen=True)
class TimeBudget:
    sus_seconds: int = 15 * 60
    hard_seconds: int = 30 * 60


class Orchestrator:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.artifacts_root = repo_root / "artifacts" / "orchestrator"
        self.state_path = self.artifacts_root / "state.json"
        self.worktrees_root = repo_root / "_worktrees" / "orchestrator"

    def load_state(self) -> dict[str, Any]:
        return _read_json(self.state_path, default={"status": "idle", "updated_at": None})

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _iso_now()
        _write_json(self.state_path, state)

    def relay_stage(self, run: SliceRun, repo_root: Path) -> dict[str, Any]:
        relay_path = (self.repo_root / "scripts" / "relay_runtime_v0.py").resolve()
        # Ensure relay is idle. If a previous run is staged/in-flight, abort+reset.
        run_state_path = repo_root / "artifacts" / "relay" / "state" / "run_state.json"
        run_state = _read_json(run_state_path, default={})
        if isinstance(run_state, dict) and run_state.get("status") not in (None, "idle"):
            _run([sys.executable, str(relay_path), "--repo-root", str(repo_root), "abort"], cwd=self.repo_root)
        _run([sys.executable, str(relay_path), "--repo-root", str(repo_root), "reset"], cwd=self.repo_root)

        cmd = [
            sys.executable,
            str(relay_path),
            "--repo-root",
            str(repo_root),
            "stage",
            "run_selected_slice_v1",
            "--slice-id",
            run.slice_id,
            "--sprint-spec-path",
            run.sprint_spec_path,
            "--declared-plane",
            run.declared_plane,
            "--baseline-branch",
            run.baseline_branch,
            "--build-branch",
            run.build_branch,
            "--retry-budget-max",
            str(run.retry_budget_max),
        ]
        if run.repo_layer:
            cmd.extend(["--repo-layer-json", json.dumps(run.repo_layer)])
        code, out, err = _run(cmd, cwd=self.repo_root)
        if code != 0:
            raise RuntimeError(f"relay stage failed (exit={code}): {err or out}".strip())

        current_job = _read_json(repo_root / "artifacts" / "relay" / "state" / "current_job.json")
        if not isinstance(current_job, dict) or not current_job.get("run_id"):
            raise RuntimeError("relay staged, but current_job.json missing or malformed")
        return current_job

    def relay_resume(self, repo_root: Path) -> tuple[int, str]:
        relay_path = (self.repo_root / "scripts" / "relay_runtime_v0.py").resolve()
        cmd = [sys.executable, str(relay_path), "--repo-root", str(repo_root), "resume"]
        code, out, err = _run(cmd, cwd=self.repo_root)
        text = (out or "") + (err or "")
        return int(code), text.strip()

    def ensure_local_baseline(self, baseline: str) -> str:
        """Relay requires baseline_branch to exist as a local head.

        If given an origin/* ref, ensure a local branch exists and return the local name.
        """
        b = baseline.strip()
        if b.startswith("origin/"):
            local = b.split("/", 1)[1]
        else:
            local = b

        # Does local branch exist?
        code, _, _ = _run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{local}"], cwd=self.repo_root)
        if code == 0:
            return local

        # Try to fetch and create a tracking branch.
        _run(["git", "fetch", "origin", local], cwd=self.repo_root)
        code2, _, err2 = _run(["git", "branch", "--track", local, f"origin/{local}"], cwd=self.repo_root)
        if code2 != 0:
            raise RuntimeError(f"could not create local baseline {local!r}: {err2}".strip())
        return local

    def _worktree_path(self, build_branch: str) -> Path:
        leaf = build_branch.split("/")[-1]
        return (self.worktrees_root / leaf).resolve()

    def _baseline_tip_sha(self, baseline_local: str) -> str:
        """Resolve baseline to a commit SHA (prefer origin/<branch>)."""
        for ref in (f"origin/{baseline_local}", baseline_local):
            code, out, err = _run(["git", "rev-parse", "--verify", ref], cwd=self.repo_root)
            if code == 0:
                return out.strip()
        raise RuntimeError(
            f"could not resolve baseline {baseline_local!r}: {err or out}".strip()
        )

    def _refresh_worktree_baseline(self, wt: Path, baseline_local: str) -> None:
        """Reset a reused worktree to the current baseline tip (stale SHAs break pytest)."""
        _run(["git", "fetch", "origin", baseline_local], cwd=self.repo_root)
        sha = self._baseline_tip_sha(baseline_local)
        code, out, err = _run(["git", "checkout", "--detach", sha], cwd=wt)
        if code != 0:
            msg = (err or out or "").strip()[-300:]
            print(f"phase_orchestrator: warn worktree refresh failed for {wt.name}: {msg}")

    def ensure_worktree(self, baseline_local: str, build_branch: str) -> Path:
        """Create (or reuse) a git worktree for the slice run.

        This prevents worker runs from switching the operator's current checkout/branch.
        When ``baseline_local`` is already checked out in another worktree (common for
        ``main``), fall back to a detached worktree at the baseline tip.
        """
        wt = self._worktree_path(build_branch)
        wt.parent.mkdir(parents=True, exist_ok=True)

        if wt.exists():
            self._refresh_worktree_baseline(wt, baseline_local)
            return wt

        # Create a new worktree checked out at the baseline branch.
        # Do NOT create the build branch here: relay preflight requires that the build branch
        # does not exist yet (the worker will create it).
        cmd = ["git", "worktree", "add", str(wt), baseline_local]
        code, out, err = _run(cmd, cwd=self.repo_root)
        combined = f"{out or ''}\n{err or ''}".lower()
        if code != 0 and "already used" in combined:
            sha = self._baseline_tip_sha(baseline_local)
            cmd = ["git", "worktree", "add", "--detach", str(wt), sha]
            code, out, err = _run(cmd, cwd=self.repo_root)
        if code != 0:
            raise RuntimeError(f"git worktree add failed: {err or out}".strip())
        return wt

    def ensure_unique_branch(self, desired: str) -> str:
        """If a branch already exists locally, append a short random suffix."""
        desired = desired.strip()
        if not desired:
            raise RuntimeError("build_branch must be non-empty")
        code, _, _ = _run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{desired}"], cwd=self.repo_root)
        if code != 0:
            return desired
        suffix = secrets.token_hex(2)
        return f"{desired}-{suffix}"

    def spawn_worker_cursor_agent(self, prompt: str, cwd: Path) -> subprocess.Popen:
        """Best-effort worker launcher.

        NOTE: Cursor Windows `cursor agent` currently appears interactive; flags like -p are not exposed.
        We still launch it and feed the prompt on stdin. If Cursor ignores stdin, the run will time out.
        """
        exe = shutil.which("cursor") or shutil.which("cursor.cmd") or "cursor"
        # On Windows, `cursor` is often a .cmd shim; that requires `shell=True`.
        if str(exe).lower().endswith(".cmd"):
            cmd: Any = f"\"{exe}\" agent"
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        else:
            proc = subprocess.Popen(
                [exe, "agent"],
                cwd=str(cwd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        try:
            if proc.stdin:
                proc.stdin.write(prompt + "\n")
                proc.stdin.flush()
        except OSError:
            pass
        return proc

    def spawn_worker_agent_cli(self, prompt: str, cwd: Path) -> subprocess.Popen:
        """Spawn the dedicated Cursor CLI (`agent`) in non-interactive mode.

        Requires prior `agent login` (or CURSOR_API_KEY / CURSOR_AUTH_TOKEN).
        """
        exe = shutil.which("agent") or "agent"
        # `--trust` prevents workspace trust prompts in headless mode.
        # `--force` allows tool execution without interactive approvals.
        cmd = [
            exe,
            "--print",
            "--output-format",
            "text",
            "--trust",
            "--force",
            "--workspace",
            str(cwd),
            prompt,
        ]
        return subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def run_slice(
        self,
        run: SliceRun,
        budgets: TimeBudget,
        worker_mode: str,
        *,
        slice_obj: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        baseline_local = self.ensure_local_baseline(run.baseline_branch)
        repo_layer = run.repo_layer
        if repo_layer is None:
            try:
                from scripts.repo_layer_paths import resolve_slice_layer_scope

                scope = resolve_slice_layer_scope(
                    self.repo_root,
                    slice_obj=slice_obj,
                    slice_id=run.slice_id,
                    declared_plane=run.declared_plane,
                )
                repo_layer = scope.to_envelope_dict()
            except (FileNotFoundError, KeyError):
                repo_layer = None

        run2 = SliceRun(
            slice_id=run.slice_id,
            sprint_spec_path=run.sprint_spec_path,
            declared_plane=run.declared_plane,
            baseline_branch=baseline_local,
            build_branch=self.ensure_unique_branch(run.build_branch),
            retry_budget_max=run.retry_budget_max,
            repo_layer=repo_layer,
        )

        self.save_state({"status": "staging", "slice_id": run2.slice_id, "build_branch": run2.build_branch})

        # Run the slice in an isolated worktree so worker tooling can't flip the operator checkout.
        wt = self.ensure_worktree(baseline_local=baseline_local, build_branch=run2.build_branch)

        # Ensure the sprint spec exists inside the worktree. If it only exists in the anchor,
        # copy it into the worktree under artifacts so staging can reference it.
        spec_in_wt = (wt / run2.sprint_spec_path).resolve()
        if not spec_in_wt.is_file():
            spec_in_anchor = (self.repo_root / run2.sprint_spec_path).resolve()
            if spec_in_anchor.is_file():
                imported_rel = Path("artifacts") / "orchestrator" / "imported_specs" / Path(run2.sprint_spec_path).name
                imported_abs = (wt / imported_rel).resolve()
                imported_abs.parent.mkdir(parents=True, exist_ok=True)
                imported_abs.write_text(spec_in_anchor.read_text(encoding="utf-8-sig"), encoding="utf-8")
                run2 = SliceRun(
                    slice_id=run2.slice_id,
                    sprint_spec_path=str(imported_rel).replace("\\", "/"),
                    declared_plane=run2.declared_plane,
                    baseline_branch=run2.baseline_branch,
                    build_branch=run2.build_branch,
                    retry_budget_max=run2.retry_budget_max,
                    repo_layer=run2.repo_layer,
                )

        job = self.relay_stage(run2, repo_root=wt)
        run_id = job["run_id"]
        expected_rel = job["expected_relay_result_path"]
        expected_path = (wt / expected_rel).resolve()

        self.save_state(
            {
                "status": "staged",
                "run_id": run_id,
                "slice_id": run2.slice_id,
                "expected_relay_result_path": expected_rel,
                "build_branch": run2.build_branch,
                "attempt": 0,
            }
        )

        layer_lines = ""
        if run2.repo_layer:
            preset = run2.repo_layer.get("layer_preset") or run2.repo_layer.get("layer")
            allowed = run2.repo_layer.get("allowed_paths") or []
            forbidden = run2.repo_layer.get("forbidden_paths") or []
            layer_lines = (
                f"\nRepo layer (hard boundary): preset={preset!r}\n"
                f"ALLOWED_PATHS: {', '.join(allowed[:12])}"
                f"{'...' if len(allowed) > 12 else ''}\n"
                f"FORBIDDEN_PATHS: {', '.join(forbidden[:12])}"
                f"{'...' if len(forbidden) > 12 else ''}\n"
                "Do not edit paths outside ALLOWED_PATHS. See docs/SOP/REPO_LAYER_MAP_V1.md.\n"
            )

        prompt = (
            "You are a worker agent executing exactly one slice under CODEX_AUTONOMY_V1 relay.\n\n"
            f"Task envelope path: artifacts/relay/runs/{run_id}/task_envelope.json\n"
            f"Expected relay result path (MUST write): {expected_rel}\n\n"
            "Read the task envelope JSON and the referenced sprint spec, execute the slice, and write relay_result.json.\n"
            f"{layer_lines}"
            "Then STOP.\n"
        )

        attempt = 0
        while True:
            attempt += 1
            self.save_state(
                {
                    "status": "worker_running",
                    "run_id": run_id,
                    "slice_id": run2.slice_id,
                    "attempt": attempt,
                    "expected_relay_result_path": expected_rel,
                    "started_at": _iso_now(),
                }
            )

            if worker_mode == "deterministic":
                from scripts.ppe_slice_worker import execute_deterministic

                execute_deterministic(
                    wt,
                    slice_id=run2.slice_id,
                    sprint_spec=run2.sprint_spec_path,
                    declared_plane=run2.declared_plane,
                    build_branch=run2.build_branch,
                    baseline_branch=run2.baseline_branch,
                    run_id=run_id,
                    expected_path=expected_path,
                    phase_plan=None,
                    slice_obj=None,
                )
                proc = None
            elif worker_mode == "cursor-agent":
                proc = self.spawn_worker_cursor_agent(prompt=prompt, cwd=wt)
            elif worker_mode == "agent-cli":
                proc = self.spawn_worker_agent_cli(prompt=prompt, cwd=wt)
            else:
                raise RuntimeError(f"unknown worker_mode {worker_mode!r}")

            # Wait for relay_result.json to appear, bounded by time budgets.
            t0 = time.time()
            sus_logged = False
            while True:
                if expected_path.is_file():
                    break

                if worker_mode == "deterministic":
                    break

                # Stream worker output head into state for debugging (best-effort, non-blocking).
                try:
                    if proc is not None and proc.stdout and not proc.stdout.closed:
                        chunk = proc.stdout.read(0)  # non-blocking in text mode; returns ''.
                        _ = chunk
                except Exception:
                    pass

                elapsed = int(time.time() - t0)
                if (not sus_logged) and elapsed >= budgets.sus_seconds:
                    sus_logged = True
                    self.save_state(
                        {
                            "status": "worker_sus_timeout",
                            "run_id": run_id,
                            "slice_id": run2.slice_id,
                            "attempt": attempt,
                            "elapsed_seconds": elapsed,
                            "expected_relay_result_path": expected_rel,
                            "note": "no relay_result.json yet; investigate",
                        }
                    )

                if worker_mode == "deterministic" and not expected_path.is_file():
                    return {
                        "status": "STOP_FOR_REVIEW",
                        "reason": "deterministic worker did not write relay_result.json",
                        "run_id": run_id,
                        "slice_id": run2.slice_id,
                        "attempt": attempt,
                    }

                if elapsed >= budgets.hard_seconds:
                    try:
                        if proc is not None:
                            proc.terminate()
                    except OSError:
                        pass
                    self.save_state(
                        {
                            "status": "worker_hard_timeout",
                            "run_id": run_id,
                            "slice_id": run2.slice_id,
                            "attempt": attempt,
                            "elapsed_seconds": elapsed,
                            "expected_relay_result_path": expected_rel,
                        }
                    )
                    return {
                        "status": "STOP_FOR_REVIEW",
                        "reason": "worker hard timeout",
                        "run_id": run_id,
                        "slice_id": run2.slice_id,
                        "attempt": attempt,
                        "expected_relay_result_path": expected_rel,
                    }

                # If the worker exits early, stop waiting and surface output.
                if proc is not None and proc.poll() is not None and not expected_path.is_file():
                    out = ""
                    try:
                        if proc.stdout:
                            out = proc.stdout.read()[:4000]
                    except OSError:
                        pass
                    self.save_state(
                        {
                            "status": "worker_exited_no_result",
                            "run_id": run_id,
                            "slice_id": run2.slice_id,
                            "attempt": attempt,
                            "output_head": out,
                        }
                    )
                    return {
                        "status": "STOP_FOR_REVIEW",
                        "reason": "worker exited without relay_result.json",
                        "run_id": run_id,
                        "slice_id": run2.slice_id,
                        "attempt": attempt,
                        "output_head": out,
                    }

                time.sleep(2)

            # Relay result exists: call resume (may be RETRY_ALLOWED and keep non-terminal).
            self.save_state({"status": "resuming", "run_id": run_id, "slice_id": run2.slice_id, "attempt": attempt})
            code, text = self.relay_resume(repo_root=wt)

            # Exit codes per relay: 0 CONTINUE, 10 RETRY_ALLOWED, 20 STOP_FOR_REVIEW, 40 BLOCKED.
            if code == 0:
                self.save_state({"status": "done_continue", "run_id": run_id, "slice_id": run2.slice_id})
                return {"status": "CONTINUE", "run_id": run_id, "slice_id": run2.slice_id, "detail": text}
            if code == 10:
                # Auto-retry up to 2 total worker attempts (user request).
                if attempt >= 2:
                    self.save_state({"status": "stop_for_review_max_attempts", "run_id": run_id, "slice_id": run2.slice_id})
                    return {
                        "status": "STOP_FOR_REVIEW",
                        "reason": "max orchestrator attempts reached after RETRY_ALLOWED",
                        "run_id": run_id,
                        "slice_id": run2.slice_id,
                        "detail": text,
                    }
                # Remove the relay_result.json so the next attempt must produce a fresh one.
                try:
                    expected_path.unlink()
                except OSError:
                    pass
                continue
            if code == 20:
                self.save_state({"status": "stop_for_review", "run_id": run_id, "slice_id": run2.slice_id})
                return {"status": "STOP_FOR_REVIEW", "run_id": run_id, "slice_id": run2.slice_id, "detail": text}
            if code == 40:
                self.save_state({"status": "blocked", "run_id": run_id, "slice_id": run2.slice_id})
                return {"status": "BLOCKED", "run_id": run_id, "slice_id": run2.slice_id, "detail": text}

            self.save_state({"status": "unexpected_relay_exit", "exit": code, "text": text})
            return {"status": "STOP_FOR_REVIEW", "reason": f"unexpected relay exit {code}", "detail": text}

    def run_phase(
        self,
        plan_path: str,
        budgets: TimeBudget,
        worker_mode: str,
    ) -> dict[str, Any]:
        """Run a phase plan (sequential slices) until stop or completion.

        Plan file format (JSON):
          {
            "phase_id": "phase_20260428_demo",
            "baseline_branch": "main" | "origin/main",
            "declared_plane": "PRODUCT-PLANE" | "EVIDENCE-PLANE",
            "slices": [
              {
                "slice_id": "...",
                "sprint_spec_path": "artifacts/phase_runs/.../slices/slice_001.md",
                "build_branch": "build/auto/...",
                "retry_budget_max": 2
              }
            ]
          }
        """
        abs_path = (self.repo_root / plan_path).resolve()
        plan = _read_json(abs_path)
        if not isinstance(plan, dict):
            raise RuntimeError(f"phase plan is not valid JSON: {plan_path}")
        phase_id = str(plan.get("phase_id") or abs_path.stem)
        baseline = str(plan.get("baseline_branch") or "main")
        plane = str(plan.get("declared_plane") or "PRODUCT-PLANE")
        slices = plan.get("slices")
        if plane not in ("PRODUCT-PLANE", "EVIDENCE-PLANE"):
            raise RuntimeError(f"plan declared_plane invalid: {plane!r}")
        if not isinstance(slices, list) or not slices:
            raise RuntimeError("plan.slices must be a non-empty list")

        results: list[dict[str, Any]] = []
        for idx, s in enumerate(slices, start=1):
            if not isinstance(s, dict):
                raise RuntimeError(f"plan.slices[{idx}] must be an object")
            run = SliceRun(
                slice_id=str(s.get("slice_id") or f"slice_{idx:03d}"),
                sprint_spec_path=str(s.get("sprint_spec_path") or ""),
                declared_plane=plane,
                baseline_branch=baseline,
                build_branch=str(s.get("build_branch") or ""),
                retry_budget_max=int(s.get("retry_budget_max") or 2),
            )
            if not run.sprint_spec_path or not run.build_branch:
                raise RuntimeError(f"slice {run.slice_id!r} missing sprint_spec_path/build_branch")

            self.save_state(
                {
                    "status": "phase_running",
                    "phase_id": phase_id,
                    "slice_index": idx,
                    "slice_total": len(slices),
                    "active_slice_id": run.slice_id,
                }
            )
            r = self.run_slice(run=run, budgets=budgets, worker_mode=worker_mode)
            results.append(r)
            if r.get("status") != "CONTINUE":
                return {"phase_id": phase_id, "status": "STOPPED", "results": results}

        return {"phase_id": phase_id, "status": "COMPLETE", "results": results}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase Orchestrator v0 (relay-gated).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("run-slice", help="Stage + run one slice through the relay.")
    sp.add_argument("--slice-id", required=True)
    sp.add_argument("--sprint-spec-path", required=True)
    sp.add_argument("--declared-plane", required=True, choices=["PRODUCT-PLANE", "EVIDENCE-PLANE"])
    sp.add_argument("--baseline-branch", required=True, help="Local branch or origin/<branch>.")
    sp.add_argument("--build-branch", required=True)
    sp.add_argument(
        "--worker-mode",
        default="agent-cli",
        choices=["agent-cli", "cursor-agent", "deterministic"],
    )
    sp.add_argument("--sus-minutes", type=int, default=15)
    sp.add_argument("--hard-minutes", type=int, default=30)
    sp.add_argument("--retry-budget-max", type=int, default=2)

    pp = sub.add_parser("run-phase", help="Run a phase plan (sequential slices) until stop.")
    pp.add_argument("--plan-path", required=True, help="Path to phase plan JSON (usually under artifacts/).")
    pp.add_argument(
        "--worker-mode",
        default="agent-cli",
        choices=["agent-cli", "cursor-agent", "deterministic"],
    )
    pp.add_argument("--sus-minutes", type=int, default=15)
    pp.add_argument("--hard-minutes", type=int, default=30)

    st = sub.add_parser("self-test", help="Run a fast relay/orchestrator self-test without LLM worker.")
    st.add_argument("--baseline-branch", default="main")
    st.add_argument("--declared-plane", default="PRODUCT-PLANE", choices=["PRODUCT-PLANE", "EVIDENCE-PLANE"])

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    repo = _repo_root(Path.cwd()) or _repo_root(Path(__file__).resolve().parent.parent)
    if repo is None:
        print("ERROR: could not locate repo root.", file=sys.stderr)
        return 2
    orch = Orchestrator(repo)

    if args.cmd == "run-slice":
        run = SliceRun(
            slice_id=args.slice_id,
            sprint_spec_path=args.sprint_spec_path,
            declared_plane=args.declared_plane,
            baseline_branch=args.baseline_branch,
            build_branch=args.build_branch,
            retry_budget_max=int(args.retry_budget_max),
        )
        budgets = TimeBudget(sus_seconds=int(args.sus_minutes) * 60, hard_seconds=int(args.hard_minutes) * 60)
        result = orch.run_slice(run=run, budgets=budgets, worker_mode=args.worker_mode)
        print(json.dumps(result, indent=2))
        # Map to relay-like exits for easy scripting.
        if result["status"] == "CONTINUE":
            return 0
        if result["status"] == "STOP_FOR_REVIEW":
            return 20
        if result["status"] == "BLOCKED":
            return 40
        return 2

    if args.cmd == "self-test":
        # Stage a minimal run in an isolated worktree and write a synthetic relay_result.json,
        # ensuring the relay decision engine works end-to-end without depending on agent tooling.
        baseline_local = orch.ensure_local_baseline(str(args.baseline_branch))
        build_branch = orch.ensure_unique_branch("build/orchestrator/selftest")
        wt = orch.ensure_worktree(baseline_local=baseline_local, build_branch=build_branch)
        # Minimal spec: reuse README as a placeholder document to satisfy "path exists".
        # (The relay only checks existence; workers interpret the contents.)
        placeholder_spec = "README.md"
        run = SliceRun(
            slice_id="Orchestrator-SelfTest",
            sprint_spec_path=placeholder_spec,
            declared_plane=str(args.declared_plane),
            baseline_branch=baseline_local,
            build_branch=build_branch,
            retry_budget_max=2,
        )
        job = orch.relay_stage(run, repo_root=wt)
        run_id = job["run_id"]
        expected_rel = job["expected_relay_result_path"]
        expected_path = (wt / expected_rel).resolve()
        expected_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "protocol": "CODEX_AUTONOMY_V1",
            "schema_version": "1",
            "slice_id": run.slice_id,
            "run_id": run_id,
            "declared_plane": run.declared_plane,
            "build_branch": run.build_branch,
            "baseline_branch": run.baseline_branch,
            "baseline_tip_before": "UNKNOWN",
            "baseline_tip_after": "UNKNOWN",
            "product_commit_sha": None,
            "preflight": {
                "build_allowed": True,
                "tree_clean": True,
                "untracked_canonical_docs": False,
                "mixed_plane_dirty": False,
                "blocker": None,
            },
            "retry_count": 0,
            "retry_budget_max": 2,
            "retry_budget_exhausted": False,
            "tests": {
                "pytest_status": "NOT_RUN",
                "pytest_count": 0,
                "ui_smoke_primary_status": "NOT_RUN",
                "ui_smoke_conditional_status": "NOT_REQUIRED",
                "ui_inspection_evidence_present": False,
                "validation_classification": "deterministic",
            },
            "tree_cleanliness": {
                "build_branch_clean": True,
                "mixed_plane_residue": False,
                "untracked_canonical_docs": False,
            },
            "promotion": {"attempted": False, "performed": False, "method": None, "ancestor_check_pass": False},
            "stop_condition": "SCOPE_AMBIGUITY",
            "ready_for_control_closeout": False,
            "safe_to_continue": False,
            "artifacts": {"ui_smoke_manifest": None, "ui_smoke_screenshot": None, "run_log": None},
            "notes": "self-test synthetic payload",
        }
        expected_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        code, text = orch.relay_resume(repo_root=wt)
        print(text)
        return code

    if args.cmd == "run-phase":
        budgets = TimeBudget(sus_seconds=int(args.sus_minutes) * 60, hard_seconds=int(args.hard_minutes) * 60)
        result = orch.run_phase(plan_path=args.plan_path, budgets=budgets, worker_mode=args.worker_mode)
        print(json.dumps(result, indent=2))
        if result["status"] == "COMPLETE":
            return 0
        return 20

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

