"""
Verify the MSOS mirror Google Doc contains a fresh regenerated timestamp.

This is a read-only helper for control-plane verification during GOOGLE_DOCS_REFRESH.
It uses the same OAuth env model as `scripts/google_docs_sync.py` and supports the
same local back-compat env keys and MCP token-store fallback.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


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


def main() -> int:
    repo_root = Path.cwd()
    _load_env_file_if_present(repo_root / ".env.mcp")

    # Back-compat / convenience mappings (match `google_docs_sync.py`).
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

    file_id = _required_env("PPE_MSOS_MIRROR_DOC_ID")
    creds = Credentials(
        token=None,
        refresh_token=_required_env("GOOGLE_OAUTH_REFRESH_TOKEN"),
        token_uri=(os.environ.get("GOOGLE_OAUTH_TOKEN_URI") or "https://oauth2.googleapis.com/token").strip(),
        client_id=_required_env("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=_required_env("GOOGLE_OAUTH_CLIENT_SECRET"),
        scopes=[
            "https://www.googleapis.com/auth/drive",
        ],
    )
    creds.refresh(Request())

    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    md = drive.files().export(fileId=file_id, mimeType="text/markdown").execute()
    if isinstance(md, bytes):
        md = md.decode("utf-8", errors="replace")
    md = str(md)

    generated_line = "NOT_FOUND"
    for ln in md.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("**Generated (UTC):**") or s.startswith("Generated (UTC):") or "Generated (UTC):" in s:
            generated_line = s
            break

    print(f"mirror_doc_id: {file_id}")
    print(f"generated_line: {generated_line}")
    if generated_line == "NOT_FOUND":
        print("ERROR: mirror export did not contain a Generated (UTC) line")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

