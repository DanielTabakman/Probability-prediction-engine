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
from scripts.ppe_operator_hint import DESKTOP_BUILD_CMD, PPE_GO_HINT, append_ppe_go_hint

HANDOFF_STATE_REL = "artifacts/orchestrator/IDE_HANDOFF_STATE.json"
HANDOFF_NOW_REL = "artifacts/orchestrator/IDE_BUILD_NOW.md"
HANDOFF_FIX_NOW_REL = "artifacts/orchestrator/IDE_FIX_NOW.md"
BUILD_LOG_REL = "artifacts/orchestrator/REMOTE_BUILD_AGENT.log"
FIX_LOG_REL = "artifacts/orchestrator/REMOTE_FIX_AGENT.log"
CONTINUITY_BRIEF_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
REMOTE_AGENT_LOGS = (BUILD_LOG_REL, FIX_LOG_REL)
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


def clipboard_on_handoff_enabled() -> bool:
    env = os.environ.get("PPE_IDE_HANDOFF_CLIPBOARD", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    return True


def explicit_prefer_ide_over_cli(repo: Path) -> bool:
    """When True, operator explicitly wants IDE handoff instead of headless CLI."""
    if os.environ.get("PPE_FORCE_CLI_BUILD", "").strip().lower() in ("1", "true", "yes", "on"):
        return False
    env = os.environ.get("PPE_PREFER_IDE_OVER_CLI", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    if os.environ.get("PPE_FORCE_IDE_HANDOFF", "").strip().lower() in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict) and handoff.get("preferIdeOverCli") is True:
            return True
    except ImportError:
        pass
    return False


def prefer_ide_over_cli(repo: Path) -> bool:
    """When True, never start headless agent CLI — use IDE handoff only."""
    if explicit_prefer_ide_over_cli(repo):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        if cfg.get("autoRemoteBuild") is False:
            return True
    except ImportError:
        pass
    return False


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


def _log_tail(repo: Path, *, log_rel: str = BUILD_LOG_REL, max_bytes: int = 8000) -> str:
    path = repo.resolve() / log_rel
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
    return any(text_indicates_usage_exhausted(_log_tail(repo, log_rel=log_rel)) for log_rel in REMOTE_AGENT_LOGS)


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


def should_attempt_headless_cli(repo: Path, *, mode: str = "build", force_handoff: bool = False) -> bool:
    """When True, try headless agent CLI before IDE handoff (build or fix)."""
    if force_handoff:
        return False
    if mode == "fix":
        if explicit_prefer_ide_over_cli(repo):
            return False
    elif prefer_ide_over_cli(repo):
        return False
    if skip_cli_when_usage_exhausted(repo) and cli_usage_exhausted(repo):
        try:
            from scripts.ppe_build_worker import codex_available, codex_cli_exhausted

            if not (codex_available() and not codex_cli_exhausted(repo)):
                return False
        except ImportError:
            return False
    if mode == "build":
        try:
            from scripts.ppe_operator_config import auto_remote_build_enabled

            if not auto_remote_build_enabled(repo):
                return False
        except ImportError:
            pass
    return True


def should_attempt_cli_build(repo: Path, *, force_handoff: bool = False) -> bool:
    return should_attempt_headless_cli(repo, mode="build", force_handoff=force_handoff)


def copy_text_to_clipboard(text: str) -> dict[str, Any]:
    if not clipboard_on_handoff_enabled():
        return {"ok": False, "skipped": True, "reason": "clipboard disabled"}
    try:
        if sys.platform == "win32":
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
                input=text,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            return {"ok": proc.returncode == 0, "platform": "windows"}
        if sys.platform == "darwin":
            proc = subprocess.run(
                ["pbcopy"],
                input=text,
                text=True,
                capture_output=True,
                check=False,
            )
            return {"ok": proc.returncode == 0, "platform": "darwin"}
        proc = subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )
        return {"ok": proc.returncode == 0, "platform": "xclip"}
    except (OSError, FileNotFoundError) as exc:
        return {"ok": False, "error": str(exc)}


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


def build_handoff_prompt(
    *,
    slice_id: str,
    starter_rel: str,
    plan_path: str,
    worker: str | None = None,
    repo: Path | None = None,
) -> str:
    from scripts.ppe_build_worker import WORKER_MANUAL, build_product_prompt, resolve_build_worker

    if worker is None and repo is not None:
        worker = str(resolve_build_worker(repo, for_handoff=True).get("worker") or WORKER_MANUAL)
    resolved_worker = worker or WORKER_MANUAL
    return build_product_prompt(
        slice_id=slice_id,
        starter_rel=starter_rel,
        plan_path=plan_path,
        worker=resolved_worker,  # type: ignore[arg-type]
    )


def write_handoff_now_doc(
    repo: Path,
    *,
    slice_id: str,
    starter_rel: str,
    plan_path: str,
    reason: str,
    worker: str | None = None,
) -> Path:
    from scripts.ppe_build_worker import WORKER_MANUAL, handoff_instructions, resolve_build_worker

    resolved = resolve_build_worker(repo, for_handoff=True)
    handoff_worker = worker or str(resolved.get("worker") or WORKER_MANUAL)
    prompt = build_handoff_prompt(
        slice_id=slice_id,
        starter_rel=starter_rel,
        plan_path=plan_path,
        worker=handoff_worker,
        repo=repo,
    )
    steps = handoff_instructions(handoff_worker)  # type: ignore[arg-type]
    numbered = "\n".join(
        [f"1. Double-click **{DESKTOP_BUILD_CMD}** (build prompt copies to clipboard)."]
        + [f"{idx}. {step}" for idx, step in enumerate(steps, start=2)]
    )
    body = "\n".join(
        [
            "# IDE BUILD — action required",
            "",
            f"**Slice:** `{slice_id}`",
            f"**Worker:** `{handoff_worker}`",
            f"**Reason:** {reason}",
            "",
            "## Do this (real PC only — not the VM)",
            "",
            numbered,
            "",
            f"Manual fallback: load only `{starter_rel}` and follow **## When done (required)**.",
            "",
            "```text",
            prompt,
            "```",
            "",
            f"Full starter: `{starter_rel}`",
            "",
            "Status: `ppe_request.cmd reconcile` → `CONTROL_PLANE_STATUS.json`",
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
    from scripts.ppe_build_worker import WORKER_MANUAL, resolve_build_worker, open_worker_for_handoff

    handoff_worker = str(resolve_build_worker(repo, for_handoff=True).get("worker") or WORKER_MANUAL)
    prompt = build_handoff_prompt(
        slice_id=slice_id,
        starter_rel=starter_rel,
        plan_path=plan_path,
        worker=handoff_worker,
        repo=repo,
    )
    now_doc = write_handoff_now_doc(
        repo,
        slice_id=slice_id,
        starter_rel=starter_rel,
        plan_path=plan_path,
        reason=reason,
        worker=handoff_worker,
    )
    clipboard = copy_text_to_clipboard(prompt)
    opened = open_worker_for_handoff(repo, worker=handoff_worker, starter_file=starter_file)  # type: ignore[arg-type]

    state = load_handoff_state(repo)
    state.update(
        {
            "last_handoff_at": _utc_now(),
            "last_handoff_slice": slice_id,
            "last_handoff_source": source,
            "last_handoff_reason": reason,
            "last_starter": starter_rel,
            "last_handoff_worker": handoff_worker,
            "worker_open": opened.get("ok"),
            "clipboard": clipboard.get("ok"),
        }
    )
    save_handoff_state(repo, state)

    from scripts.ppe_ide_build_automation_trigger import notify_automation

    automation = notify_automation(
        repo,
        handoff={
            "slice_id": slice_id,
            "plan_path": plan_path,
            "starter": starter_rel,
            "reason": reason,
            "source": source,
            "force": force,
        },
    )

    title = f"PPE IDE BUILD: {slice_id}"
    clip_note = " Prompt copied to clipboard." if clipboard.get("ok") else ""
    auto_note = ""
    wh = automation.get("webhook") if isinstance(automation, dict) else None
    if isinstance(wh, dict) and not wh.get("ok") and not wh.get("skipped"):
        try:
            from scripts.ppe_ide_build_automation_health import classify_webhook_failure

            code = classify_webhook_failure(wh)
            auto_note = f"\nAutomation: {code} — run check_ide_build_automation.cmd"
        except ImportError:
            auto_note = "\nAutomation webhook failed — run check_ide_build_automation.cmd"
    body = append_ppe_go_hint(
        f"{reason}\n{HANDOFF_NOW_REL}.{clip_note}{auto_note}",
        "IDE_BUILD",
        repo=repo,
    )
    notified = False
    # Watch/loop paths already push IDE_BUILD alerts; phone build gets notify_command_result.
    skip_push = source in ("auto-watch", "loop-guard")
    if not skip_push and notify_enabled() and ntfy_configured():
        notified = send_ntfy(title, body, tags=["ppe", "ide", OUTBOUND_TAG], priority="high")

    return {
        "action": "ide_handoff",
        "mode": "ide_handoff",
        "started": True,
        "slice_id": slice_id,
        "plan_path": plan_path,
        "starter": starter_rel,
        "now_doc": str(now_doc.relative_to(repo)).replace("\\", "/"),
        "worker": handoff_worker,
        "worker_open": opened,
        "clipboard": clipboard,
        "source": source,
        "reason": reason,
        "notified": notified,
        "automation": automation,
        "message": f"IDE handoff ready for {slice_id}. {PPE_GO_HINT}",
    }


def fix_handoff_recently_done(repo: Path, verdict: str) -> bool:
    state = load_handoff_state(repo)
    if str(state.get("last_fix_handoff_verdict") or "") != verdict:
        return False
    at_raw = str(state.get("last_fix_handoff_at") or "").strip()
    if not at_raw:
        return False
    try:
        at = datetime.fromisoformat(at_raw.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - at).total_seconds()
        return age < _handoff_debounce_sec()
    except ValueError:
        return False


def write_fix_handoff_now_doc(
    repo: Path,
    *,
    verdict: str,
    blocker: str,
    reason: str,
    prompt: str,
) -> Path:
    brief_rel = CONTINUITY_BRIEF_REL
    body = "\n".join(
        [
            "# IDE FIX — action required",
            "",
            f"**Verdict:** `{verdict}`",
            f"**Blocker:** {blocker or '—'}",
            f"**Reason:** {reason}",
            "",
            "## Do this in a new Cursor Agent thread",
            "",
            f"1. `@` `{brief_rel}`",
            "2. Paste the prompt below (or say: investigate and fix the blocker).",
            "",
            "```text",
            prompt,
            "```",
            "",
            f"Continuity brief: `{brief_rel}`",
        ]
    )
    out = repo / HANDOFF_FIX_NOW_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body + "\n", encoding="utf-8")
    return out


def launch_ide_fix_handoff(
    repo: Path,
    *,
    verdict: str,
    blocker: str,
    prompt: str,
    source: str,
    reason: str,
    force: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    if not ide_handoff_enabled(repo):
        return {
            "action": "ide_fix_handoff",
            "started": False,
            "reason": "IDE handoff disabled (PPE_IDE_HANDOFF=0)",
            "verdict": verdict,
        }

    if not force and fix_handoff_recently_done(repo, verdict):
        return {
            "action": "ide_fix_handoff",
            "started": False,
            "reason": f"fix handoff already done recently for {verdict}",
            "verdict": verdict,
            "debounced": True,
        }

    brief_file = repo / CONTINUITY_BRIEF_REL.replace("/", os.sep)
    now_doc = write_fix_handoff_now_doc(
        repo,
        verdict=verdict,
        blocker=blocker,
        reason=reason,
        prompt=prompt,
    )
    clipboard = copy_text_to_clipboard(prompt)
    cursor = open_cursor_for_handoff(repo, brief_file if brief_file.is_file() else now_doc)

    state = load_handoff_state(repo)
    state.update(
        {
            "last_fix_handoff_at": _utc_now(),
            "last_fix_handoff_verdict": verdict,
            "last_fix_handoff_source": source,
            "last_fix_handoff_reason": reason,
            "cursor_open": cursor.get("ok"),
            "clipboard": clipboard.get("ok"),
        }
    )
    save_handoff_state(repo, state)

    title = f"PPE IDE FIX: {verdict}"
    clip_note = " Prompt copied to clipboard." if clipboard.get("ok") else ""
    body = (
        f"{reason}\n"
        f"{blocker or 'Investigate operator blocker.'}\n"
        f"Open Cursor → new Agent thread → @{CONTINUITY_BRIEF_REL}\n"
        f"Shortcut: {HANDOFF_FIX_NOW_REL}.{clip_note}"
    )
    notified = False
    if notify_enabled() and ntfy_configured():
        notified = send_ntfy(title, body, tags=["ppe", "ide", OUTBOUND_TAG], priority="high")

    return {
        "action": "ide_fix_handoff",
        "mode": "ide_handoff",
        "started": True,
        "verdict": verdict,
        "blocker": blocker,
        "now_doc": str(now_doc.relative_to(repo)).replace("\\", "/"),
        "cursor": cursor,
        "clipboard": clipboard,
        "source": source,
        "reason": reason,
        "notified": notified,
        "message": f"IDE fix handoff ready for {verdict} — open Agent thread with @{CONTINUITY_BRIEF_REL}",
    }


def headless_cli_skip_reason(repo: Path, *, try_cli: bool, cli_out: dict[str, Any]) -> str:
    from scripts.ppe_build_worker import codex_available, collect_build_worker_status
    from scripts.ppe_remote_agent import agent_available

    if prefer_ide_over_cli(repo):
        status = collect_build_worker_status(repo)
        worker = status.get("handoff_worker") or "manual"
        return f"near-zero API profile — use desktop BUILD ({worker})"
    if cli_usage_exhausted(repo):
        if codex_available():
            return "Cursor CLI out of usage — desktop BUILD will use Codex when configured"
        return "agent CLI out of usage — use desktop BUILD (Cursor or Codex)"
    if not agent_available() and codex_available():
        return "Cursor CLI not installed — Codex CLI available for headless or desktop BUILD"
    if not agent_available() and not codex_available():
        return "No headless BUILD worker — use desktop BUILD (install Cursor agent or codex CLI)"
    if not try_cli:
        return "CLI skipped — use desktop BUILD"
    return str(cli_out.get("reason") or "CLI unavailable")


def respond_to_ide_build(
    repo: Path,
    *,
    source: str,
    note: str = "",
    force_handoff: bool = False,
) -> dict[str, Any]:
    """Try headless CLI when allowed; otherwise surface IDE handoff."""
    from scripts.ppe_remote_agent_dispatch import respond_remote_agent

    return respond_remote_agent(
        repo,
        mode="build",
        source=source,
        note=note,
        force_handoff=force_handoff,
    )


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
    handoff_info = job.get("handoff") or {}
    build_worker = str(job.get("build_worker") or handoff_info.get("build_worker") or "cursor-cli")
    if text_indicates_usage_exhausted(combined):
        if build_worker == "codex-cli":
            from scripts.ppe_build_worker import mark_codex_usage_exhausted

            mark_codex_usage_exhausted(repo, detail=stderr or detail[-300:])
        else:
            mark_cli_usage_exhausted(repo, detail=stderr or detail[-300:])

    if not ide_handoff_enabled(repo):
        return None

    mode = str(handoff_info.get("mode") or "build").strip().lower()
    if mode == "build" and build_worker == "cursor-cli":
        from scripts.ppe_build_worker import WORKER_CODEX_CLI, codex_available, codex_cli_exhausted
        from scripts.ppe_remote_build_agent import launch_build

        if codex_available() and not codex_cli_exhausted(repo):
            fallback = launch_build(
                repo,
                note="cursor CLI failed — codex fallback",
                source=str(handoff_info.get("source") or "cli-failure"),
                worker=WORKER_CODEX_CLI,
            )
            if fallback.get("started"):
                return fallback

    reason = "agent CLI out of usage" if cli_usage_exhausted(repo) else "agent CLI failed"

    mode = str(handoff_info.get("mode") or "build").strip().lower()
    if mode == "fix":
        verdict = str(handoff_info.get("verdict") or "").strip()
        if not verdict:
            return None
        from scripts.ppe_remote_fix_agent import build_fix_prompt

        prompt = build_fix_prompt(
            repo,
            user_note=str(handoff_info.get("user_note") or ""),
        )
        return launch_ide_fix_handoff(
            repo,
            verdict=verdict,
            blocker=str(handoff_info.get("blocker") or ""),
            prompt=prompt,
            source=str(handoff_info.get("source") or "cli-failure"),
            reason=reason,
            force=True,
        )

    slice_id = str(handoff_info.get("slice_id") or "").strip()
    plan_path = str(handoff_info.get("plan_path") or "").strip()
    if not slice_id or not plan_path:
        return None
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
