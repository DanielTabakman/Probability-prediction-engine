"""Best-effort Google Docs refresh when the BUILD queue goes idle."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def idle_refresh_enabled() -> bool:
    v = os.environ.get("PPE_GOOGLE_DOCS_ON_IDLE", "").strip().lower()
    return v not in {"0", "false", "no"}


def _mcp_refresh_token() -> str | None:
    token_path = Path.home() / ".config" / "google-docs-mcp" / "token.json"
    try:
        obj = json.loads(token_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    v = str(obj.get("refresh_token") or "").strip()
    return v or None


def mirror_credentials_configured() -> bool:
    mirror = (os.environ.get("PPE_MSOS_MIRROR_DOC_ID") or os.environ.get("MSOS_REPO_TRUTH_DOC_ID") or "").strip()
    if not mirror:
        return False
    client_id = (os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or os.environ.get("GOOGLE_CLIENT_ID") or "").strip()
    client_secret = (
        os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or os.environ.get("GOOGLE_CLIENT_SECRET") or ""
    ).strip()
    refresh = (
        os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN") or os.environ.get("GOOGLE_REFRESH_TOKEN") or ""
    ).strip() or (_mcp_refresh_token() or "")
    return bool(client_id and client_secret and refresh)


def _load_local_env(repo: Path) -> None:
    env_mcp = repo / ".env.mcp"
    if not env_mcp.is_file():
        return
    try:
        text = env_mcp.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"')
        if k and k not in os.environ:
            os.environ[k] = v


def _run_script(repo: Path, script: str, extra_argv: list[str]) -> tuple[int, str]:
    cmd = [sys.executable, str(repo / "scripts" / script), "--repo-root", str(repo), *extra_argv]
    proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def refresh_google_docs_on_queue_idle(repo_root: Path, *, reason: str) -> dict[str, Any]:
    """
    Called when auto-chain has no next READY queue chapter.

    Always regenerates local MSOS snapshot artifacts.
    Pushes to the MSOS mirror Google Doc when OAuth credentials are configured.
    Never fails the BUILD wrapper (best-effort).
    """
    repo = repo_root.resolve()
    result: dict[str, Any] = {
        "reason": reason,
        "skipped": False,
        "snapshot_ok": False,
        "mirror_ok": False,
        "mirror_attempted": False,
    }

    if not idle_refresh_enabled():
        result["skipped"] = True
        result["skip_note"] = "PPE_GOOGLE_DOCS_ON_IDLE=0"
        print("ppe_google_docs: skip (PPE_GOOGLE_DOCS_ON_IDLE disabled)")
        return result

    print(f"ppe_google_docs: queue idle — refreshing MSOS mirror ({reason})")
    _load_local_env(repo)

    snap_rc, snap_out = _run_script(repo, "sync_msos_repo_truth.py", [])
    result["snapshot_ok"] = snap_rc == 0
    result["snapshot_exit_code"] = snap_rc
    if snap_out:
        print(snap_out)

    if not mirror_credentials_configured():
        result["mirror_note"] = "mirror push skipped (OAuth / PPE_MSOS_MIRROR_DOC_ID not configured)"
        print(f"ppe_google_docs: {result['mirror_note']}")
        _write_idle_report(repo, result)
        return result

    result["mirror_attempted"] = True
    mirror_rc, mirror_out = _run_script(
        repo,
        "google_docs_sync.py",
        ["--sync-repo-to-mirror", "--write-report"],
    )
    result["mirror_ok"] = mirror_rc == 0
    result["mirror_exit_code"] = mirror_rc
    if mirror_out:
        print(mirror_out)
    if mirror_rc != 0:
        print("ppe_google_docs: WARN mirror push failed (BUILD idle continues)")

    _write_idle_report(repo, result)
    return result


def _write_idle_report(repo: Path, result: dict[str, Any]) -> None:
    out = repo / "artifacts" / "control_plane" / "google_docs_idle_refresh.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"ppe_google_docs: wrote {out}")
