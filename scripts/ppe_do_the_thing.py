"""Do The Thing — accumulated operator actions + smart status-derived plan, one button."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_autobuilder import (
    ACTION_ADVANCE,
    ACTION_FINISH_PENDING,
    ACTION_HANDOFF,
    ACTION_RUN_LOCAL,
    PHASE_AWAITING_BUILD,
    PHASE_CLOSEOUT_PENDING,
    PHASE_DEGRADED,
    PHASE_RUN_LOCAL_PENDING,
    PHASE_STACK_DOWN,
    action_advance,
    action_finish_pending,
    action_handoff,
    action_run_local,
    collect_autobuilder_status,
)
from scripts.ppe_desktop_auto_operator import _maybe_git_pull
from scripts.ppe_operator_vm_ssh import fetch_vm_brief, ssh_vm, vm_advance_command, vm_finish_command
from scripts.ppe_operator_shortcuts import detect_role

QUEUE_REL = "artifacts/orchestrator/DO_THE_THING_QUEUE.json"
LOG_REL = "artifacts/orchestrator/DO_THE_THING.log"
BUTTON_NAME = "DO THE THING"

ALLOWED_ACTIONS = frozenset(
    {
        "advance",
        "autobuilder:advance",
        "autobuilder:ensure",
        "autobuilder:finish-pending",
        "autobuilder:handoff",
        "autobuilder:retry-build",
        "autobuilder:run-local",
        "desktop_build",
        "desktop_continue",
        "git_pull",
        "vm_advance",
        "vm_finish",
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def queue_path(repo: Path) -> Path:
    return (repo / QUEUE_REL).resolve()


def log_path(repo: Path) -> Path:
    return (repo / LOG_REL).resolve()


def _append_log(repo: Path, line: str) -> None:
    path = log_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{_utc_now()} {line}\n")


def load_queue(repo: Path) -> dict[str, Any]:
    path = queue_path(repo)
    if not path.is_file():
        return {"version": 1, "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "items": []}
    if not isinstance(data, dict):
        return {"version": 1, "items": []}
    items = data.get("items")
    if not isinstance(items, list):
        data["items"] = []
    return data


def save_queue(repo: Path, data: dict[str, Any]) -> None:
    path = queue_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["version"] = 1
    data["updatedAt"] = _utc_now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def add_queue_item(
    repo: Path,
    *,
    action: str,
    label: str = "",
    source: str = "operator",
) -> dict[str, Any]:
    action = str(action or "").strip()
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"unknown action {action!r}; allowed: {sorted(ALLOWED_ACTIONS)}")
    data = load_queue(repo)
    item = {
        "id": uuid.uuid4().hex[:12],
        "action": action,
        "label": (label or action).strip(),
        "source": source.strip() or "operator",
        "addedAt": _utc_now(),
    }
    items = list(data.get("items") or [])
    if not any(str(x.get("action") or "") == action for x in items if isinstance(x, dict)):
        items.append(item)
    data["items"] = items
    save_queue(repo, data)
    _append_log(repo, f"queued action={action} source={source} label={label!r}")
    return item


def clear_queue(repo: Path) -> None:
    save_queue(repo, {"version": 1, "items": []})


def _dedupe_plan(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action") or "").strip()
        if not action or action in seen:
            continue
        seen.add(action)
        out.append(item)
    return out


def derive_actions(repo: Path) -> list[dict[str, Any]]:
    """Status-derived plan when the queue is empty."""
    repo = repo.resolve()
    role = detect_role(repo)
    status = collect_autobuilder_status(repo)
    phase = str(status.get("phase") or "")
    verdict = str(status.get("verdict") or "")
    closeout = status.get("closeout") or {}

    derived: list[dict[str, Any]] = []

    if role == "daily_driver":
        if verdict == "IDE_BUILD" or phase in (PHASE_AWAITING_BUILD, PHASE_DEGRADED):
            derived.append(
                {
                    "action": "desktop_build",
                    "label": "Open IDE BUILD in Cursor (product slice)",
                    "derived": True,
                }
            )
        if phase == PHASE_CLOSEOUT_PENDING or closeout.get("pending"):
            derived.append(
                {
                    "action": "desktop_continue",
                    "label": "Pull main, mark product ready, continue relay on VM",
                    "derived": True,
                }
            )
        elif verdict == "RUN_LOCAL" or phase == PHASE_RUN_LOCAL_PENDING:
            derived.append(
                {
                    "action": "desktop_continue",
                    "label": "Continue relay on VM (finish_ide_build)",
                    "derived": True,
                }
            )
        if phase == PHASE_STACK_DOWN:
            derived.append(
                {
                    "action": "vm_advance",
                    "label": "VM stack down — restart/advance on loop host",
                    "derived": True,
                }
            )
    else:
        derived.append(
            {
                "action": "advance",
                "label": f"Autobuilder advance (phase={phase}, verdict={verdict})",
                "derived": True,
            }
        )

    return _dedupe_plan(derived)


def resolve_plan(repo: Path, *, include_derived: bool = True) -> list[dict[str, Any]]:
    data = load_queue(repo)
    queued = [x for x in (data.get("items") or []) if isinstance(x, dict)]
    if queued:
        return _dedupe_plan(queued)
    if include_derived:
        return derive_actions(repo)
    return []


def _run_git_pull(repo: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "pull", "origin", "main"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "action": "git_pull",
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "").strip()[-500:],
        "stderr": (proc.stderr or "").strip()[-500:],
    }


def _execute_action(repo: Path, item: dict[str, Any]) -> dict[str, Any]:
    action = str(item.get("action") or "").strip()
    label = str(item.get("label") or action)
    if action not in ALLOWED_ACTIONS:
        return {"action": action, "ok": False, "error": "action not allowed"}

    _append_log(repo, f"run action={action} label={label!r}")

    if action == "git_pull":
        return _run_git_pull(repo)

    if action == "desktop_build":
        result = action_handoff(repo)
        return {"action": action, "ok": True, **result}

    if action == "desktop_continue":
        pull = _run_git_pull(repo)
        ssh = ssh_vm(vm_finish_command(pull_main=True))
        status = fetch_vm_brief(repo, use_cache=False)
        ok = pull.get("ok") and ssh.get("ok")
        return {
            "action": action,
            "ok": ok,
            "git_pull": pull,
            "vm_finish": ssh,
            "vm_status": status,
        }

    if action == "vm_finish":
        ssh = ssh_vm(vm_finish_command())
        return {"action": action, "ok": ssh.get("ok"), **ssh}

    if action == "vm_advance":
        ssh = ssh_vm(vm_advance_command())
        return {"action": action, "ok": ssh.get("ok"), **ssh}

    if action == "advance" or action == "autobuilder:advance":
        result = action_advance(repo)
        skipped = bool(result.get("skipped"))
        return {"action": action, "ok": not skipped or result.get("action") == ACTION_ADVANCE, **result}

    autobuilder_map = {
        "autobuilder:handoff": action_handoff,
        "autobuilder:finish-pending": action_finish_pending,
        "autobuilder:run-local": action_run_local,
    }
    if action in autobuilder_map:
        result = autobuilder_map[action](repo)
        return {"action": action, "ok": True, **result}

    if action == "autobuilder:ensure":
        from scripts.ppe_autobuilder import action_ensure

        result = action_ensure(repo)
        return {"action": action, "ok": True, **result}

    if action == "autobuilder:retry-build":
        from scripts.ppe_autobuilder import action_retry_build

        result = action_retry_build(repo)
        return {"action": action, "ok": True, **result}

    return {"action": action, "ok": False, "error": "unhandled"}


def run_plan(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    role = detect_role(repo)
    plan = resolve_plan(repo)
    had_queued = bool(load_queue(repo).get("items"))

    result: dict[str, Any] = {
        "button": BUTTON_NAME,
        "role": role,
        "dry_run": dry_run,
        "had_queued_items": had_queued,
        "plan": [{"action": x.get("action"), "label": x.get("label")} for x in plan],
        "results": [],
    }

    if not plan:
        result["ok"] = True
        result["skipped"] = True
        result["message"] = "Nothing to do — queue empty and no derived actions."
        return result

    if dry_run:
        result["ok"] = True
        return result

    if role == "daily_driver":
        _maybe_git_pull(repo)

    all_ok = True
    for item in plan:
        step = _execute_action(repo, item)
        result["results"].append(step)
        if not step.get("ok"):
            all_ok = False
            break

    result["ok"] = all_ok
    if all_ok and had_queued:
        clear_queue(repo)
        _append_log(repo, "queue cleared after successful run")
    elif all_ok:
        _append_log(repo, "derived plan completed (queue was empty)")

    return result


def format_plan_brief(plan: list[dict[str, Any]]) -> str:
    if not plan:
        return f"{BUTTON_NAME}: nothing queued."
    lines = [f"{BUTTON_NAME} — {len(plan)} step(s):"]
    for i, item in enumerate(plan, 1):
        lines.append(f"  {i}. {item.get('label') or item.get('action')}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Do The Thing — operator action queue + one-button run")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Queue an action for the next button press")
    p_add.add_argument("action", choices=sorted(ALLOWED_ACTIONS))
    p_add.add_argument("--label", default="", help="Human-readable step label")
    p_add.add_argument("--source", default="operator")

    sub.add_parser("list", help="Show queued + derived plan")
    sub.add_parser("clear", help="Clear the queue without running")

    p_run = sub.add_parser("run", help="Execute queued plan (or derived actions if queue empty)")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if not args.command:
        plan = resolve_plan(repo)
        print(format_plan_brief(plan))
        return 0

    if args.command == "add":
        item = add_queue_item(repo, action=args.action, label=args.label, source=args.source)
        print(json.dumps(item, indent=2))
        return 0

    if args.command == "clear":
        clear_queue(repo)
        print("do_the_thing: queue cleared")
        return 0

    if args.command == "list":
        plan = resolve_plan(repo)
        data = load_queue(repo)
        out = {"queued_count": len(data.get("items") or []), "plan": plan}
        print(json.dumps(out, indent=2))
        print()
        print(format_plan_brief(plan))
        return 0

    if args.command == "run":
        out = run_plan(repo, dry_run=args.dry_run)
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            for step in out.get("results") or []:
                status = "OK" if step.get("ok") else "FAIL"
                print(f"  [{status}] {step.get('action')}")
            if out.get("skipped"):
                print(out.get("message"))
            elif out.get("ok"):
                print(f"\n{BUTTON_NAME}: done.")
                if out.get("had_queued_items"):
                    print("Queue cleared.")
            else:
                print(f"\n{BUTTON_NAME}: stopped on failure — see {LOG_REL}")
        return 0 if out.get("ok") else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
