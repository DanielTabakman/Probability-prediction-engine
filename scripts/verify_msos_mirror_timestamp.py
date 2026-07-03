"""
Verify the MSOS mirror Google Doc contains a fresh regenerated timestamp.

This is a read-only helper for control-plane verification during GOOGLE_DOCS_REFRESH.
It uses the same OAuth env model as `scripts/google_docs_sync.py` and supports the
same local back-compat env keys and MCP token-store fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from scripts.google_oauth_scopes import SYNC_GOOGLE_SCOPES

DEFAULT_MAX_AGE_HOURS = 24
_GENERATED_RE = re.compile(
    r"Generated\s*\(UTC\)\s*:\s*\**\s*([0-9T:\-+Z.]+)",
    re.IGNORECASE,
)


def _load_env_file_if_present(env_path: Path) -> None:
    try:
        text = env_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k or k in os.environ:
            continue
        if len(v) >= 2 and v[0] == v[-1] == '"':
            v = v[1:-1]
        os.environ[k] = v


def _mcp_refresh_token() -> str | None:
    token_path = Path.home() / ".config" / "google-docs-mcp" / "token.json"
    try:
        obj = json.loads(token_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    v = str(obj.get("refresh_token") or "").strip()
    return v or None


def _required_env(name: str) -> str:
    v = (os.environ.get(name) or "").strip()
    if not v:
        raise SystemExit(f"ERROR: missing required env var {name}")
    return v


def _bootstrap_oauth_env() -> None:
    if not (os.environ.get("PPE_MSOS_MIRROR_DOC_ID") or "").strip():
        legacy = (os.environ.get("MSOS_REPO_TRUTH_DOC_ID") or "").strip()
        if legacy:
            os.environ["PPE_MSOS_MIRROR_DOC_ID"] = legacy

    if not (os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or "").strip():
        v = (os.environ.get("GOOGLE_CLIENT_ID") or "").strip()
        if v:
            os.environ["GOOGLE_OAUTH_CLIENT_ID"] = v
    if not (os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip():
        v = (os.environ.get("GOOGLE_CLIENT_SECRET") or "").strip()
        if v:
            os.environ["GOOGLE_OAUTH_CLIENT_SECRET"] = v
    if not (os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN") or "").strip():
        v = (os.environ.get("GOOGLE_REFRESH_TOKEN") or "").strip()
        if v:
            os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"] = v
    if not (os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN") or "").strip():
        v = _mcp_refresh_token()
        if v:
            os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"] = v


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip().strip("*").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def extract_generated_timestamp(markdown: str) -> tuple[str, datetime | None]:
    generated_line = "NOT_FOUND"
    generated_at: datetime | None = None
    for ln in markdown.splitlines():
        s = ln.strip()
        if not s:
            continue
        if "Generated (UTC):" in s or "generated (utc):" in s.lower():
            generated_line = s
            match = _GENERATED_RE.search(s)
            if match:
                generated_at = _parse_utc(match.group(1))
            break
    return generated_line, generated_at


def fetch_mirror_markdown() -> tuple[str, str]:
    file_id = _required_env("PPE_MSOS_MIRROR_DOC_ID")
    creds = Credentials(
        token=None,
        refresh_token=_required_env("GOOGLE_OAUTH_REFRESH_TOKEN"),
        token_uri=(os.environ.get("GOOGLE_OAUTH_TOKEN_URI") or "https://oauth2.googleapis.com/token").strip(),
        client_id=_required_env("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=_required_env("GOOGLE_OAUTH_CLIENT_SECRET"),
        scopes=list(SYNC_GOOGLE_SCOPES),
    )
    creds.refresh(Request())

    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    md = drive.files().export(fileId=file_id, mimeType="text/markdown").execute()
    if isinstance(md, bytes):
        md = md.decode("utf-8", errors="replace")
    return file_id, str(md)


def verify_mirror_freshness(*, max_age_hours: float = DEFAULT_MAX_AGE_HOURS) -> dict[str, object]:
    file_id, markdown = fetch_mirror_markdown()
    generated_line, generated_at = extract_generated_timestamp(markdown)
    now = datetime.now(timezone.utc)
    age_hours: float | None = None
    fresh = False
    if generated_at is not None:
        age_hours = max(0.0, (now - generated_at).total_seconds()) / 3600.0
        fresh = age_hours <= max(0.0, float(max_age_hours))
    return {
        "mirror_doc_id": file_id,
        "generated_line": generated_line,
        "generated_at": generated_at.isoformat().replace("+00:00", "Z") if generated_at else None,
        "age_hours": round(age_hours, 2) if age_hours is not None else None,
        "max_age_hours": max_age_hours,
        "fresh": fresh,
        "ok": generated_at is not None and fresh,
    }


def maybe_notify_mirror_stale(report: dict[str, object]) -> bool:
    if report.get("ok"):
        return False
    title = "PPE MSOS Google mirror stale"
    body = (
        f"Live Mirror doc timestamp stale or missing.\n"
        f"generated_line: {report.get('generated_line')}\n"
        f"age_hours: {report.get('age_hours')} (max {report.get('max_age_hours')})"
    )
    try:
        from scripts.ppe_notify_push import ntfy_topic_stuck, send_ntfy_to_topic

        return bool(
            send_ntfy_to_topic(
                ntfy_topic_stuck(),
                title=title,
                body=body,
                priority="high",
                tags=["mirror", "google", "warning"],
            )
        )
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify MSOS Live Mirror Google Doc timestamp freshness")
    ap.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    ap.add_argument("--notify-on-fail", action="store_true", help="Send ntfy when stale (needs local notify env)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    _load_env_file_if_present(Path.cwd() / ".env.mcp")
    _bootstrap_oauth_env()

    report = verify_mirror_freshness(max_age_hours=args.max_age_hours)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"mirror_doc_id: {report.get('mirror_doc_id')}")
        print(f"generated_line: {report.get('generated_line')}")
        print(f"age_hours: {report.get('age_hours')} (max {report.get('max_age_hours')})")
        print(f"fresh: {report.get('fresh')}")

    if not report.get("ok"):
        if args.notify_on_fail:
            maybe_notify_mirror_stale(report)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
