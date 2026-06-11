"""IDE handoff when headless agent CLI cannot run (e.g. out of usage)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_ide_build_starter import starter_path, write_starter
from scripts.ppe_notify_push import OUTBOUND_TAG, ntfy_configured, notify_enabled, send_ntfy

HANDOFF_STATE_REL = "artifacts/orchestrator/IDE_HANDOFF_STATE.json"
HANDOFF_NOW_REL = "artifacts/orchestrator/IDE_BUILD_NOW.md"
BUILD_LOG_REL = "artifacts/orchestrator/REMOTE_BUILD_AGENT.log"
USAGE_MARKERS = (
    "out of usage",
    "usage limit",
    "increase your limit",
    "rate limit",
    "quota",
)

DEFAULT_HANDOFF_DEBOUNCE_SEC = 1800


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def handoff_state_path(repo: Path) -> Path:
    return repo.resolve() / HANDOFF_STATE_REL


def load_handoff_state(repo: Path) -> dict[str, Any]:
    path = handoff_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_handoff_state(repo: Path, state: dict[str, Any]) -> None:
    path = handoff_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def ide_handoff_enabled(repo: Path) -> bool:
    env = os.environ.get("PPE_IDE_HANDOFF", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict) and handoff.get("enabled") is False:
            return False
        if handoff is False:
            return False
    except ImportError:
        pass
    return True


def open_cursor_on_handoff(repo: Path) -> bool:
    env = os.environ.get("PPE_IDE_HANDOFF_OPEN", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict) and handoff.get("openCursor") is False:
            return False
    except ImportError:
        pass
    return True


def skip_cli_when_usage_exhausted(repo: Path) -> bool:
    env = os.environ.get("PPE_SKIP_CLI_WHEN_USAGE_EXHAUSTED", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict) and handoff.get("skipCliWhenUsageExhausted") is False:
            return False
    except ImportError:
        pass
    return True


def _log_tail(repo: Path, *, max_bytes: int = 8000) -> str:
    path = repo.resolve() / BUILD_LOG_REL
    if not path.is_file():
        return ""
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if len(data) > max_bytes:
        data = data[-max_bytes:]
    return data.decode("utf-8", errors="replace")


def text_indicates_usage_exhausted(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in USAGE_MARKERS)


def cli_usage_exhausted(repo: Path) -> bool:
    if os.environ.get("PPE_FORCE_CLI_BUILD", "").strip().lower() in ("1", "true", "yes", "on"):
        return False
    state = load_handoff_state(repo)
    if state.get("cli_usage_exhausted"):
        return True
    return text_indicates_usage_exhausted(_log_tail(repo))


def mark_cli_usage_exhausted(repo: Path, *, detail: str = "") -> None:
    state = load_handoff_state(repo)
    state.update(
        {
            "cli_usage_exhausted": True,
            "cli_usage_exhausted_at": _utc_now(),
            "cli_usage_detail": detail[:500] if detail else state.get("cli_usage_detail"),
        }
    )
    save_handoff_state(repo, state)


def clear_cli_usage_exhausted(repo: Path) -> None:
    state = load_handoff_state(repo)
    state.pop("cli_usage_exhausted", None)
    state.pop("cli_usage_exhausted_at", None)
    state.pop("cli_usage_detail", None)
    save_handoff_state(repo, state)


def should_attempt_cli_build(repo: Path, *, force_handoff: bool = False) -> bool:
    if force_handoff or os.environ.get("PPE_FORCE_IDE_HANDOFF", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        return False
    if skip_cli_when_usage_exhausted(repo) and cli_usage_exhausted(repo):
        return False
    return True


def _handoff_debounce_sec() -> int:
    try:
        return max(60, int(os.environ.get("PPE_IDE_HANDOFF_DEBOUNCE_SEC", str(DEFAULT_HANDOFF_DEBOUNCE_SEC))))
    except ValueError:
        return DEFAULT_HANDOFF_DEBOUNCE_SEC


def handoff_recently_done(repo: Path, slice_id: str) -> bool:
    state = load_handoff_state(repo)
    if str(state.get("last_handoff_slice") or "") != slice_id:
        return False
    at_raw = str(state.get("last_handoff_at") or "").strip()
    if not at_raw:
        return False
    try:
        at = datetime.fromisoformat(at_raw.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - at).total_seconds()
        return age < _handoff_debounce_sec()
    except ValueError:
        return False


def resolve_cursor_executable() -> str | None:
    exe = shutil.which("cursor")
    if exe:
        return exe
    local = os.environ.get("LOCALAPPDATA", "").strip()
    candidates: list[Path] = []
    if local:
        candidates.extend(
            [
                Path(local) / "Programs" / "cursor" / "Cursor.exe",
                Path(local) / "Programs" / "Cursor" / "Cursor.exe",
            ]
        )
    program_files = os.environ.get("ProgramFiles", "").strip()
    if program_files:
        candidates.append(Path(program_files) / "Cursor" / "Cursor.exe")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _detached_open(cmd: list[str], *, cwd: Path) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "cwd": cwd,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
    else:
        kwargs["start_new_session"] = True
    try:
        proc = subprocess.Popen(cmd, **kwargs)
        return {"ok": True, "pid": proc.pid, "cmd": cmd}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "cmd": cmd}


def open_cursor_for_handoff(repo: Path, starter_file: Path) -> dict[str, Any]:
    if not open_cursor_on_handoff(repo):
        return {"ok": False, "skipped": True, "reason": "PPE_IDE_HANDOFF_OPEN disabled"}
    exe = resolve_cursor_executable()
    if not exe:
        return {"ok": False, "reason": "Cursor executable not found (install Cursor IDE)"}
    repo = repo.resolve()
    starter_file = starter_file.resolve()
    # Open workspace then starter (reuse window when supported).
    opened = _detached_open([exe, str(repo)], cwd=repo)
    if starter_file.is_file():
        _detached_open([exe, "-r", str(starter_file)], cwd=repo)
    return opened


def build_handoff_prompt(*, slice_id: str, starter_rel: str, plan_path: str) -> str:
    return "\n".join(
        [
            f"Build product slice **{slice_id}**.",
            f"Load ONLY `@{starter_rel}`.",
            f"Phase plan: `{plan_path}`.",
            "",
            "When done, in order:",
            "1. python scripts/run_pushable_gate.py",
            "2. git commit on plan buildBranch",
            f"3. mark_ide_product_ready.cmd {slice_id} {plan_path}",
            "4. run_ppe_local.cmd",
            "",
            "Execute autonomously; do not ask for confirmation.",
        ]
    )


def write_handoff_now_doc(
    repo: Path,
    *,
    slice_id: str,
    starter_rel: str,
    plan_path: str,
    reason: str,
) -> Path:
    prompt = build_handoff_prompt(slice_id=slice_id, starter_rel=starter_rel, plan_path=plan_path)
    body = "\n".join(
        [
            "# IDE BUILD — action required",
            "",
            f"**Slice:** `{slice_id}`",
            f"**Reason:** {reason}",
            "",
            "## Do this in a new Cursor Agent thread",
            "",
            f"1. `@` `{starter_rel}`",
            "2. Paste the prompt below (or say: build this slice per the starter).",
            "",
            "```text",
            prompt,
            "```",
            "",
            f"Full starter: `{starter_rel}`",
        ]
    )
    out = repo / HANDOFF_NOW_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body + "\n", encoding="utf-8")
    return out


def launch_ide_handoff(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    source: str,
    reason: str,
    force: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    if not ide_handoff_enabled(repo):
        return {
            "action": "ide_handoff",
            "started": False,
            "reason": "IDE handoff disabled (PPE_IDE_HANDOFF=0)",
            "slice_id": slice_id,
        }

    if not force and handoff_recently_done(repo, slice_id):
        return {
            "action": "ide_handoff",
            "started": False,
            "reason": f"handoff already done recently for {slice_id}",
            "slice_id": slice_id,
            "debounced": True,
        }

    write_starter(repo, slice_id=slice_id, phase_plan=plan_path)
    starter_rel = starter_path(slice_id)
    starter_file = repo / starter_rel.replace("/", os.sep)
    now_doc = write_handoff_now_doc(
        repo,
        slice_id=slice_id,
        starter_rel=starter_rel,
        plan_path=plan_path,
        reason=reason,
    )
    cursor = open_cursor_for_handoff(repo, starter_file)

    state = load_handoff_state(repo)
    state.update(
        {
            "last_handoff_at": _utc_now(),
            "last_handoff_slice": slice_id,
            "last_handoff_source": source,
            "last_handoff_reason": reason,
            "last_starter": starter_rel,
            "cursor_open": cursor.get("ok"),
        }
    )
    save_handoff_state(repo, state)

    title = f"PPE IDE BUILD: {slice_id}"
    body = (
        f"Headless agent CLI unavailable ({reason}).\n"
        f"Open Cursor → new Agent thread → @{starter_rel}\n"
        f"Shortcut: {HANDOFF_NOW_REL}"
    )
    notified = False
    if notify_enabled() and ntfy_configured():
        notified = send_ntfy(title, body, tags=["ppe", "ide", OUTBOUND_TAG], priority="high")

    return {
        "action": "ide_handoff",
        "mode": "ide_handoff",
        "started": True,
        "slice_id": slice_id,
        "plan_path": plan_path,
        "starter": starter_rel,
        "now_doc": str(now_doc.relative_to(repo)).replace("\\", "/"),
        "cursor": cursor,
        "source": source,
        "reason": reason,
        "notified": notified,
        "message": f"IDE handoff ready for {slice_id} — open Agent thread with @{starter_rel}",
    }


def respond_to_ide_build(
    repo: Path,
    *,
    source: str,
    note: str = "",
    force_handoff: bool = False,
) -> dict[str, Any]:
    """Try headless CLI when allowed; otherwise surface IDE handoff."""
    from scripts.ppe_remote_agent import agent_available
    from scripts.ppe_remote_build_agent import launch_build, read_build_lock, resolve_build_target

    repo = repo.resolve()
    target = resolve_build_target(repo)
    if not target.get("ok"):
        return {"action": "ide_build", "started": False, **target}
    if target.get("mode") == "run_local":
        return launch_build(repo, note=note, source=source)

    slice_id = str(target["slice_id"])
    plan_path = str(target["plan_path"])

    if read_build_lock(repo):
        return {
            "action": "ide_build",
            "started": False,
            "reason": f"build already in flight for {slice_id}",
            "slice_id": slice_id,
        }

    try_cli = (
        should_attempt_cli_build(repo, force_handoff=force_handoff)
        and agent_available()
        and not force_handoff
    )
    if try_cli:
        out = launch_build(repo, note=note, source=source)
        if out.get("started"):
            return out
        reason = str(out.get("reason") or "CLI build did not start")

    if cli_usage_exhausted(repo):
        reason = "agent CLI out of usage — use Cursor IDE Agent"
    elif not agent_available():
        reason = "agent CLI not installed — use Cursor IDE Agent"
    elif not try_cli:
        reason = "CLI build skipped — use Cursor IDE Agent"
    else:
        reason = str(out.get("reason") or "CLI build unavailable")

    handoff = launch_ide_handoff(
        repo,
        slice_id=slice_id,
        plan_path=plan_path,
        source=source,
        reason=reason,
        force=force_handoff,
    )
    handoff["cli_attempted"] = try_cli
    return handoff


def maybe_handoff_after_cli_failure(repo: Path, job: dict[str, Any], result: dict[str, Any]) -> dict[str, Any] | None:
    """After detached CLI worker fails, mark usage exhaustion and hand off to IDE."""
    if result.get("ok"):
        return None
    log_path = repo / "artifacts" / "orchestrator" / str(job.get("log_name") or "REMOTE_BUILD_AGENT.log")
    detail = ""
    if log_path.is_file():
        try:
            detail = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            detail = ""
    stderr = str(result.get("stderr_head") or "")
    combined = f"{detail}\n{stderr}"
    if text_indicates_usage_exhausted(combined):
        mark_cli_usage_exhausted(repo, detail=stderr or detail[-300:])

    handoff_info = job.get("handoff") or {}
    slice_id = str(handoff_info.get("slice_id") or "").strip()
    plan_path = str(handoff_info.get("plan_path") or "").strip()
    if not slice_id or not plan_path:
        return None
    if not ide_handoff_enabled(repo):
        return None

    reason = "agent CLI build failed"
    if cli_usage_exhausted(repo):
        reason = "agent CLI out of usage"
    return launch_ide_handoff(
        repo,
        slice_id=slice_id,
        plan_path=plan_path,
        source=str(handoff_info.get("source") or "cli-failure"),
        reason=reason,
        force=True,
    )


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(description="IDE handoff for IDE_BUILD product slices")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--respond", action="store_true", help="Respond to current IDE_BUILD verdict")
    ap.add_argument("--force-handoff", action="store_true", help="Skip CLI; open IDE handoff only")
    ap.add_argument("--slice-id", default="")
    ap.add_argument("--phase-plan", default="")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.respond:
        result = respond_to_ide_build(repo, source="manual", force_handoff=args.force_handoff)
        print(json.dumps(result, indent=2))
        return 0 if result.get("started") else 1

    if args.slice_id and args.phase_plan:
        result = launch_ide_handoff(
            repo,
            slice_id=args.slice_id,
            plan_path=args.phase_plan,
            source="manual",
            reason="manual IDE handoff",
            force=True,
        )
        print(json.dumps(result, indent=2))
        return 0 if result.get("started") else 1

    print("ppe_ide_handoff: use --respond or --slice-id + --phase-plan", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
