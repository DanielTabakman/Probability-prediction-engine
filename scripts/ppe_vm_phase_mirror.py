"""Git-tracked VM phase mirror + FINISH_IN_FLIGHT ntfy heartbeat (loop host only)."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VM_OPERATOR_PHASE_REL = "docs/SOP/VM_OPERATOR_PHASE.json"
PHASE_NOTIFY_STATE_REL = "artifacts/control_plane/VM_PHASE_NOTIFY_STATE.json"
IN_FLIGHT_SINCE_REL = "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json"
STUCK_NOTIFY_STATE_REL = "artifacts/control_plane/VM_IN_FLIGHT_STUCK_NOTIFY.json"
MIRROR_PUBLISH_STATE_REL = "artifacts/control_plane/VM_MIRROR_PUBLISH_STATE.json"

IN_FLIGHT_PHASES = frozenset({"FINISH_IN_FLIGHT", "BUILD_IN_FLIGHT"})
PHASE_NOTIFY_COOLDOWN_SECONDS = 900
IN_FLIGHT_STUCK_SECONDS = 2700
MIRROR_PUBLISH_COOLDOWN_SECONDS = 90
MIRROR_HEARTBEAT_PUBLISH_SECONDS = 600


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def mirror_path(repo: Path) -> Path:
    return (repo / VM_OPERATOR_PHASE_REL).resolve()


def notify_state_path(repo: Path) -> Path:
    return (repo / PHASE_NOTIFY_STATE_REL).resolve()


def in_flight_since_path(repo: Path) -> Path:
    return (repo / IN_FLIGHT_SINCE_REL).resolve()


def stuck_notify_state_path(repo: Path) -> Path:
    return (repo / STUCK_NOTIFY_STATE_REL).resolve()


def load_vm_phase_mirror(repo: Path) -> dict[str, Any] | None:
    path = mirror_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _is_loop_host(repo: Path) -> bool:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        return bool(loop_host_start_allowed()[0])
    except Exception:
        return False


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def write_vm_phase_mirror(repo: Path, status: dict[str, Any]) -> Path | None:
    if not _is_loop_host(repo):
        return None
    phase = str(status.get("phase") or "").strip()
    if not phase:
        return None
    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    payload = {
        "version": 1,
        "description": (
            "Git-tracked VM autobuilder phase mirror — loop host writes on phase change; "
            "desktop reads via git pull."
        ),
        "as_of": str(status.get("as_of") or _utc_now()),
        "phase": phase,
        "verdict": str(status.get("verdict") or "").strip(),
        "chapter_name": operator.get("chapter_name"),
        "phase_plan_path": operator.get("phase_plan_path"),
        "recommended_action": status.get("recommended_action"),
    }
    path = mirror_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _mirror_fingerprint(payload: dict[str, Any]) -> str:
    return "|".join(
        [
            str(payload.get("phase") or ""),
            str(payload.get("verdict") or ""),
            str(payload.get("chapter_name") or ""),
            str(payload.get("phase_plan_path") or ""),
        ]
    )


def _heartbeat_publish_due(
    payload: dict[str, Any],
    prior: dict[str, Any],
    *,
    fingerprint: str,
) -> bool:
    phase = str(payload.get("phase") or "")
    if phase not in IN_FLIGHT_PHASES:
        return False
    last_ok = prior.get("last_publish_ok")
    if last_ok is False:
        return True
    last_at = _parse_utc(str(prior.get("last_publish_at") or ""))
    if last_at is None:
        return True
    elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
    if elapsed >= MIRROR_HEARTBEAT_PUBLISH_SECONDS:
        return True
    if str(prior.get("fingerprint") or "") != fingerprint:
        return True
    mirror_as_of = _parse_utc(str(payload.get("as_of") or ""))
    if mirror_as_of and last_at and mirror_as_of > last_at:
        return True
    return False


def maybe_commit_publish_vm_mirror(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_loop_host(repo):
        return {"skipped": True, "reason": "not_loop_host"}

    fp = _mirror_fingerprint(payload)
    state_path = repo / MIRROR_PUBLISH_STATE_REL
    prior: dict[str, Any] = {}
    if state_path.is_file():
        try:
            prior = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}

    heartbeat_due = _heartbeat_publish_due(payload, prior, fingerprint=fp)
    if heartbeat_due:
        payload = {**payload, "as_of": _utc_now()}
    if fp == str(prior.get("fingerprint") or "") and not heartbeat_due:
        last_at = _parse_utc(str(prior.get("last_publish_at") or ""))
        if last_at is not None and prior.get("last_publish_ok") is not False:
            elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
            if elapsed < MIRROR_PUBLISH_COOLDOWN_SECONDS:
                return {"skipped": True, "reason": "unchanged", "fingerprint": fp}

    rel = VM_OPERATOR_PHASE_REL.replace("\\", "/")
    mirror_file = mirror_path(repo)
    if heartbeat_due and mirror_file.is_file():
        mirror_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    diff = _git(repo, "diff", "--name-only", "--", rel)
    untracked = _git(repo, "ls-files", "--others", "--exclude-standard", "--", rel)
    has_change = bool((diff.stdout or "").strip()) or bool((untracked.stdout or "").strip())
    if not has_change:
        if heartbeat_due:
            mirror_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            diff = _git(repo, "diff", "--name-only", "--", rel)
            has_change = bool((diff.stdout or "").strip())
        if not has_change:
            return {"skipped": True, "reason": "no_git_diff", "fingerprint": fp, "heartbeat_due": heartbeat_due}

    stage = _git(repo, "add", "--", rel)
    if stage.returncode != 0:
        return {"ok": False, "error": (stage.stderr or "git add failed").strip()}

    phase = str(payload.get("phase") or "unknown")
    commit = _git(repo, "commit", "-m", f"ops: vm phase mirror {phase}")
    if commit.returncode != 0:
        err = (commit.stderr or commit.stdout or "").strip()
        if "nothing to commit" in err.lower():
            return {"skipped": True, "reason": "nothing_to_commit"}
        return {"ok": False, "error": err}

    publish: dict[str, Any] = {"skipped": True, "reason": "publish_disabled"}
    publish_ok = False
    try:
        from scripts.ppe_operator_git_sync import publish_vm_mirror_ahead

        publish = publish_vm_mirror_ahead(repo, phase=phase)
        publish_ok = bool(publish.get("ok"))
        pr_url = str(publish.get("pr_url") or "").strip()
        if publish_ok and pr_url:
            _maybe_notify_mirror_pr_opened(repo, phase=phase, pr_url=pr_url)
        if publish_ok:
            try:
                from scripts.ppe_operator_git_sync import close_conflicting_mirror_prs

                close_conflicting_mirror_prs(repo)
            except Exception:
                pass
    except Exception as exc:
        publish = {"ok": False, "error": str(exc)}

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "fingerprint": fp,
                "last_publish_at": _utc_now(),
                "last_publish_ok": publish_ok,
                "phase": phase,
                "heartbeat_due": heartbeat_due,
                "publish": publish,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "ok": publish_ok or bool(commit.returncode == 0),
        "fingerprint": fp,
        "commit": True,
        "publish": publish,
        "heartbeat_due": heartbeat_due,
    }


def _maybe_notify_mirror_pr_opened(repo: Path, *, phase: str, pr_url: str) -> bool:
    state_path = repo / "artifacts/control_plane/VM_MIRROR_PR_NOTIFY.json"
    prior: dict[str, Any] = {}
    if state_path.is_file():
        try:
            prior = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}
    if str(prior.get("pr_url") or "") == pr_url:
        return False
    title = f"PPE VM mirror PR: {phase.replace('_', ' ')}"
    body = f"Loop host published phase mirror — desktop: git pull origin main after merge.\n{pr_url}"
    try:
        from scripts.ppe_notify_push import send_ntfy

        sent = send_ntfy(title, body, priority="low", tags=["mirror", "pr"], click_url=pr_url)
    except Exception:
        return False
    if sent:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps({"pr_url": pr_url, "phase": phase, "notified_at": _utc_now()}, indent=2) + "\n",
            encoding="utf-8",
        )
    return sent


def _load_notify_state(repo: Path) -> dict[str, Any]:
    path = notify_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_notify_state(repo: Path, state: dict[str, Any]) -> None:
    path = notify_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def maybe_notify_in_flight_phase(repo: Path, status: dict[str, Any]) -> bool:
    if not _is_loop_host(repo):
        return False
    phase = str(status.get("phase") or "").strip()
    if phase not in IN_FLIGHT_PHASES:
        return False

    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    chapter = str(operator.get("chapter_name") or operator.get("phase_plan_path") or "relay").strip()
    fingerprint = f"{phase}|{chapter}|{status.get('verdict')}"
    prior = _load_notify_state(repo)
    if fingerprint == str(prior.get("fingerprint") or ""):
        last_at = _parse_utc(str(prior.get("last_notified_at") or ""))
        if last_at is not None:
            elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
            if elapsed < PHASE_NOTIFY_COOLDOWN_SECONDS:
                return False

    title = f"PPE {phase.replace('_', ' ').title()}"
    body = f"{chapter} — VM loop running; desktop: wait or DESKTOP_CONTINUE when due."
    try:
        from scripts.ppe_notify_push import send_ntfy

        send_ntfy(title=title, body=body, priority="low", tags=["hourglass_flowing_sand"])
    except Exception:
        return False

    _save_notify_state(
        repo,
        {
            "fingerprint": fingerprint,
            "last_notified_at": _utc_now(),
            "phase": phase,
            "chapter": chapter,
        },
    )
    return True


def _load_in_flight_since(repo: Path) -> dict[str, Any]:
    path = in_flight_since_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_in_flight_since(repo: Path, state: dict[str, Any]) -> None:
    path = in_flight_since_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def track_in_flight_since(repo: Path, status: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_loop_host(repo):
        return None
    phase = str(status.get("phase") or "").strip()
    prior = _load_in_flight_since(repo)
    if phase in IN_FLIGHT_PHASES:
        if str(prior.get("phase") or "") != phase:
            state = {
                "phase": phase,
                "since": _utc_now(),
                "verdict": str(status.get("verdict") or ""),
                "chapter_name": (status.get("operator") or {}).get("chapter_name"),
            }
            _save_in_flight_since(repo, state)
            return state
        return prior
    if prior:
        _save_in_flight_since(repo, {})
    return None


def maybe_notify_stuck_in_flight(
    repo: Path,
    status: dict[str, Any],
    *,
    stuck_seconds: int = IN_FLIGHT_STUCK_SECONDS,
) -> bool:
    if not _is_loop_host(repo):
        return False
    phase = str(status.get("phase") or "").strip()
    if phase not in IN_FLIGHT_PHASES:
        return False
    since_state = _load_in_flight_since(repo)
    since_at = _parse_utc(str(since_state.get("since") or ""))
    if since_at is None:
        return False
    elapsed = (datetime.now(timezone.utc) - since_at).total_seconds()
    if elapsed < max(300, int(stuck_seconds)):
        return False

    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    chapter = str(operator.get("chapter_name") or operator.get("phase_plan_path") or "relay").strip()
    fingerprint = f"stuck|{phase}|{chapter}"
    stuck_path = stuck_notify_state_path(repo)
    prior: dict[str, Any] = {}
    if stuck_path.is_file():
        try:
            prior = json.loads(stuck_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}
    if fingerprint == str(prior.get("fingerprint") or ""):
        return False

    mins = int(elapsed // 60)
    title = f"PPE stuck: {phase.replace('_', ' ').title()}"
    body = (
        f"{chapter} — in-flight {mins}m. VM: POST_BUILD_FINISH.log / fix_vm_operator.cmd. "
        "Desktop: Remote-SSH ppe-vm or one status SSH."
    )
    try:
        from scripts.ppe_notify_push import ntfy_topic_stuck, send_ntfy_to_topic

        send_ntfy_to_topic(
            ntfy_topic_stuck(),
            title=title,
            body=body,
            priority="high",
            tags=["warning", "rotating_light", "stuck"],
        )
    except Exception:
        return False

    stuck_path.parent.mkdir(parents=True, exist_ok=True)
    stuck_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "last_notified_at": _utc_now(),
                "elapsed_seconds": elapsed,
                "phase": phase,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return True


def sync_autobuilder_phase_artifacts(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    mirror = write_vm_phase_mirror(repo, status)
    payload = load_vm_phase_mirror(repo) or {}
    publish = maybe_commit_publish_vm_mirror(repo, payload) if mirror else {"skipped": True}
    notified = maybe_notify_in_flight_phase(repo, status)
    track_in_flight_since(repo, status)
    stuck_notified = maybe_notify_stuck_in_flight(repo, status)
    auto_advance: dict[str, Any] = {"skipped": True}
    try:
        from scripts.ppe_factory_throughput import assess_factory_throughput, maybe_auto_advance_stuck

        operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
        light_status = {
            "verdict": status.get("verdict") or operator.get("verdict"),
            "phase_plan_path": operator.get("phase_plan_path"),
            "chapter_name": operator.get("chapter_name"),
            "supply": operator.get("supply") or {},
        }
        ft = assess_factory_throughput(repo, light_status)
        auto_advance = maybe_auto_advance_stuck(repo, ft)
    except Exception:
        pass
    return {
        "mirror_path": str(mirror) if mirror else None,
        "publish": publish,
        "notified": notified,
        "stuck_notified": stuck_notified,
        "auto_advance": auto_advance,
    }
