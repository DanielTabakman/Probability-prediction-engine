"""
google_docs_sync.py

Automations:
1) Sync PPE Master (Google Doc) -> repo file `docs/VISION/PPE_MASTER_MVP1.md`
2) Sync repo MSOS snapshot -> MSOS mirror Google Doc marker block

This script uses the Google Docs + Drive APIs directly (not MCP) so it can run
in GitHub Actions with credentials from secrets.

Credential model (recommended):
- OAuth client id/secret + refresh token for a user that can access the docs.

Required env vars (CI-friendly):
- PPE_MASTER_DOC_ID
- PPE_MSOS_MIRROR_DOC_ID
- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET
- GOOGLE_OAUTH_REFRESH_TOKEN

Notes:
- We update the MSOS mirror by replacing the plain-text marker block range.
  Formatting is intentionally minimal; the goal is truthful freshness.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Ensure `import scripts.*` works when invoked as `python scripts/google_docs_sync.py`.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.google_oauth_scopes import SYNC_GOOGLE_SCOPES
from scripts.msos.repo_truth_snapshot import build_repo_truth_snapshot  # noqa: E402


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _required_env(name: str) -> str:
    v = (os.environ.get(name) or "").strip()
    if not v:
        raise SystemExit(f"ERROR: missing required env var {name}")
    return v


def _load_env_file_if_present(env_path: Path) -> None:
    """
    Best-effort local convenience for Cursor runs.

    - Loads KEY=VALUE lines from an env file (e.g. repo-root `.env.mcp`) into `os.environ`
      *only if* the key is not already set.
    - Ignores blank lines and `#` comments.
    - Does not print values.
    """
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
    """
    Best-effort: reuse the local google-docs-mcp token store if present.

    Path matches `docs/SOP/MCP_GOOGLE_DOCS_SETUP.md` and `scripts/set_google_docs_secrets_once.ps1`.
    """
    token_path = Path.home() / ".config" / "google-docs-mcp" / "token.json"
    try:
        obj = json.loads(token_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    v = str(obj.get("refresh_token") or "").strip()
    return v or None


# CI sync uses minimal scopes (see scripts/google_oauth_scopes.py). MCP tokens may
# include broader grants; refresh still works when the token is a superset.

def _oauth_creds() -> Credentials:
    client_id = _required_env("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = _required_env("GOOGLE_OAUTH_CLIENT_SECRET")
    refresh_token = _required_env("GOOGLE_OAUTH_REFRESH_TOKEN")
    token_uri = (os.environ.get("GOOGLE_OAUTH_TOKEN_URI") or "https://oauth2.googleapis.com/token").strip()

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=list(SYNC_GOOGLE_SCOPES),
    )
    creds.refresh(Request())
    return creds


def _docs_service(creds: Credentials):
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def _drive_service(creds: Credentials):
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _drive_export_markdown(drive, *, file_id: str) -> str:
    # Docs export as text/markdown (Drive API).
    data = drive.files().export(fileId=file_id, mimeType="text/markdown").execute()
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    # googleapiclient may return str for small payloads
    return str(data)


def _write_repo_master(*, repo_root: Path, markdown: str, source_doc_id: str) -> Path:
    out_path = repo_root / "docs" / "VISION" / "PPE_MASTER_MVP1.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = "\n".join(
        [
            "---",
            'title: "PPE Master (MVP1 controlling canon)"',
            f'source_google_doc_id: "{source_doc_id}"',
            f'imported_utc: "{_utc_now_iso()}"',
            "---",
            "",
        ]
    )

    # If the exported markdown already contains a YAML frontmatter block, strip it to avoid nesting.
    stripped = re.sub(r"(?s)\A---\n.*?\n---\n+", "", markdown).lstrip()
    out_path.write_text(header + stripped + ("\n" if not stripped.endswith("\n") else ""), encoding="utf-8")
    return out_path


@dataclass(frozen=True)
class MarkerRange:
    start: int
    end: int


def _iter_text_runs(doc: dict[str, Any]) -> Iterable[tuple[int, int, str]]:
    """
    Yields (startIndex, endIndex, text) for each textRun.
    """
    for el in (doc.get("body", {}) or {}).get("content", []) or []:
        para = el.get("paragraph")
        if not para:
            continue
        for pe in para.get("elements") or []:
            tr = (pe.get("textRun") or {}).get("content")
            if tr is None:
                continue
            yield int(pe.get("startIndex") or 0), int(pe.get("endIndex") or 0), str(tr)


def _find_marker_range(doc: dict[str, Any], *, start_marker: str, end_marker: str) -> MarkerRange:
    """
    Find character index range [start,end) to replace, inclusive of markers and their surrounding content.

    We find the first occurrence of start_marker and the next occurrence of end_marker *after* it,
    based on the concatenated text stream.
    """
    # Build a streaming view: we need absolute indices.
    runs = list(_iter_text_runs(doc))
    full = "".join(t for _, _, t in runs)
    s_pos = full.find(start_marker)
    if s_pos < 0:
        raise SystemExit(f"ERROR: start marker {start_marker!r} not found in MSOS mirror doc")
    e_pos = full.find(end_marker, s_pos)
    if e_pos < 0:
        raise SystemExit(f"ERROR: end marker {end_marker!r} not found after start marker in MSOS mirror doc")

    # Convert full-string positions back to doc character indices (1-based in API).
    # We walk runs, tracking cumulative string position and mapping to the startIndex.
    cum = 0
    start_idx = None
    end_idx = None
    for run_start, run_end, text in runs:
        run_len = len(text)
        # full positions map into [cum, cum+run_len)
        if start_idx is None and s_pos >= cum and s_pos < cum + run_len:
            start_idx = run_start + (s_pos - cum)
        if end_idx is None and e_pos >= cum and e_pos < cum + run_len:
            end_idx = run_start + (e_pos - cum) + len(end_marker)
        cum += run_len
        if start_idx is not None and end_idx is not None:
            break

    if start_idx is None or end_idx is None:
        raise SystemExit("ERROR: failed to map marker positions to doc indices")
    if end_idx <= start_idx:
        raise SystemExit("ERROR: invalid marker range computed")
    return MarkerRange(start=int(start_idx), end=int(end_idx))


def _replace_doc_range_plaintext(docs, *, document_id: str, start: int, end: int, text: str) -> None:
    # Delete + insert (batchUpdate).
    reqs: list[dict[str, Any]] = [
        {"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}},
        {"insertText": {"location": {"index": start}, "text": text}},
    ]
    docs.documents().batchUpdate(documentId=document_id, body={"requests": reqs}).execute()


def sync_master_to_repo(*, repo_root: Path, master_doc_id: str) -> dict[str, Any]:
    creds = _oauth_creds()
    drive = _drive_service(creds)
    md = _drive_export_markdown(drive, file_id=master_doc_id)
    out_path = _write_repo_master(repo_root=repo_root, markdown=md, source_doc_id=master_doc_id)
    return {"ok": True, "wrote": str(out_path.as_posix())}


def sync_repo_to_msos_mirror(*, repo_root: Path, mirror_doc_id: str) -> dict[str, Any]:
    creds = _oauth_creds()
    docs = _docs_service(creds)

    snap = build_repo_truth_snapshot(repo_root=repo_root)
    # Replace the marker block with the snapshot markdown (plain text insertion).
    doc = docs.documents().get(documentId=mirror_doc_id).execute()
    rng = _find_marker_range(doc, start_marker="MSOS_REPO_TRUTH_AUTO_START", end_marker="MSOS_REPO_TRUTH_AUTO_END")

    _replace_doc_range_plaintext(
        docs,
        document_id=mirror_doc_id,
        start=rng.start,
        end=rng.end,
        text=snap.snapshot_markdown,
    )
    return {"ok": True, "updated_doc_id": mirror_doc_id, "generated_at_utc": snap.generated_at_utc}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sync PPE Google Docs <-> repo")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--sync-master-to-repo", action="store_true")
    ap.add_argument("--sync-repo-to-mirror", action="store_true")
    ap.add_argument("--write-report", action="store_true", help="Write artifacts/control_plane/google_docs_sync_report.json")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    os.environ.setdefault("PYTHONPATH", str(repo))
    _load_env_file_if_present(repo / ".env.mcp")

    # Back-compat: some local env files use older mirror key names.
    if not (os.environ.get("PPE_MSOS_MIRROR_DOC_ID") or "").strip():
        legacy = (os.environ.get("MSOS_REPO_TRUTH_DOC_ID") or "").strip()
        if legacy:
            os.environ["PPE_MSOS_MIRROR_DOC_ID"] = legacy

    # Back-compat: OAuth env names (match scripts/set_google_docs_secrets_once.ps1 behavior).
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

    master_id = os.environ.get("PPE_MASTER_DOC_ID") or ""
    mirror_id = os.environ.get("PPE_MSOS_MIRROR_DOC_ID") or ""

    report: dict[str, Any] = {"generated_at_utc": _utc_now_iso(), "ok": True, "actions": {}}
    try:
        if args.sync_master_to_repo:
            report["actions"]["sync_master_to_repo"] = sync_master_to_repo(repo_root=repo, master_doc_id=_required_env("PPE_MASTER_DOC_ID"))
        if args.sync_repo_to_mirror:
            report["actions"]["sync_repo_to_mirror"] = sync_repo_to_msos_mirror(
                repo_root=repo, mirror_doc_id=_required_env("PPE_MSOS_MIRROR_DOC_ID")
            )
        if not args.sync_master_to_repo and not args.sync_repo_to_mirror:
            ap.print_help()
            return 2
    except HttpError as e:
        report["ok"] = False
        report["error"] = f"google_api_http_error: {e}"
        print(f"ERROR: Google API failure: {e}")
        return 1
    except SystemExit as e:
        report["ok"] = False
        report["error"] = str(e)
        raise
    finally:
        if args.write_report:
            out = repo / "artifacts" / "control_plane" / "google_docs_sync_report.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"google_docs_sync: wrote {out}")

    print("google_docs_sync: OK")
    if master_id:
        print(f"google_docs_sync: PPE_MASTER_DOC_ID={master_id}")
    if mirror_id:
        print(f"google_docs_sync: PPE_MSOS_MIRROR_DOC_ID={mirror_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

