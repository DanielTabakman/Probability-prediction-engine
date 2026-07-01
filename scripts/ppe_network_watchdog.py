"""Desktop VM network watchdog — SSH probe + ntfy after consecutive failures (not relay)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_REL = "artifacts/control_plane/NETWORK_WATCHDOG_STATE.json"
DEFAULT_FAIL_THRESHOLD = 3


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, state: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def probe_vm_ssh(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_operator_vm_ssh import VM_SSH_HOST, ssh_vm

        ssh = ssh_vm("echo PPE_NET_OK", timeout=20)
        ok = bool(ssh.get("ok") and "PPE_NET_OK" in str(ssh.get("stdout") or ""))
        return {
            "ok": ok,
            "host": VM_SSH_HOST,
            "detail": (ssh.get("stderr") or ssh.get("stdout") or "")[:160],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def run_network_watchdog(
    repo: Path,
    *,
    fail_threshold: int = DEFAULT_FAIL_THRESHOLD,
    notify: bool = True,
) -> dict[str, Any]:
    repo = repo.resolve()
    prior = load_state(repo)
    probe = probe_vm_ssh(repo)
    consecutive = int(prior.get("consecutive_failures") or 0)
    if probe.get("ok"):
        consecutive = 0
        recovered = bool(prior.get("alert_sent"))
    else:
        consecutive += 1
        recovered = False

    alert_sent = bool(prior.get("alert_sent"))
    notified = False
    if (
        notify
        and not probe.get("ok")
        and consecutive >= max(1, int(fail_threshold))
        and not alert_sent
    ):
        try:
            from scripts.ppe_notify_push import ntfy_topic_stuck, send_ntfy_to_topic

            host = str(probe.get("host") or "ppe-vm")
            detail = str(probe.get("detail") or probe.get("error") or "SSH failed")[:120]
            title = f"PPE network: VM unreachable ({host})"
            body = (
                f"{consecutive} failed SSH probes. Check Tailscale/VPN and {host}. "
                f"Detail: {detail}"
            )
            notified = send_ntfy_to_topic(
                ntfy_topic_stuck(),
                title,
                body,
                priority="high",
                tags=["network", "warning"],
            )
            if notified:
                alert_sent = True
        except Exception:
            pass

    if probe.get("ok") and recovered:
        alert_sent = False

    state = {
        "as_of": _utc_now(),
        "last_ok": probe.get("ok"),
        "consecutive_failures": consecutive,
        "alert_sent": alert_sent,
        "last_probe": probe,
    }
    save_state(repo, state)
    return {
        "probe": probe,
        "consecutive_failures": consecutive,
        "threshold": fail_threshold,
        "notified": notified,
        "state": state,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Probe VM SSH reachability; ntfy after N failures")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--threshold", type=int, default=DEFAULT_FAIL_THRESHOLD)
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    os.environ.setdefault("PPE_REPO_ROOT", str(repo))
    try:
        from scripts.ppe_notify_push import bootstrap_operator_notify_env

        bootstrap_operator_notify_env(repo)
    except Exception:
        pass
    report = run_network_watchdog(
        repo,
        fail_threshold=args.threshold,
        notify=not args.no_notify,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        probe = report.get("probe") or {}
        mark = "OK" if probe.get("ok") else "FAIL"
        print(f"network watchdog: {mark} consecutive_failures={report.get('consecutive_failures')}")
    return 0 if (report.get("probe") or {}).get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
