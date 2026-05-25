"""sync_msos_repo_truth_v1 — push repo snapshot to MSOS Google Doc (markers only)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from scripts.msos.build_snapshot import MARKER_END, MARKER_START, build_and_write

ENV_MCP = ".env.mcp"
TOKEN_REL = ".config/google-docs-mcp/token.json"
REPORT_REL = "artifacts/control_plane/msos_sync_report.json"


def _parse_env_mcp(repo: Path) -> dict[str, str]:
    env_path = repo / ENV_MCP
    out: dict[str, str] = {}
    if not env_path.is_file():
        return out
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out


def _token_path() -> Path:
    profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
    return Path(profile) / TOKEN_REL


def _load_google_credentials(client_id: str, client_secret: str, token_file: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError as e:
        raise ImportError(
            "Install google-docs-sync extras: pip install -e '.[google-docs-sync]'"
        ) from e

    # Match @a-bonus/google-docs-mcp OAuth scopes (token refresh rejects narrower scopes).
    scopes = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]
    if not token_file.is_file():
        raise RuntimeError(
            f"Missing OAuth token at {token_file}; run scripts/auth_google_docs_mcp.ps1"
        )

    raw = json.loads(token_file.read_text(encoding="utf-8"))
    token_uri = raw.get("token_uri", "https://oauth2.googleapis.com/token")

    # MCP auth often stores only refresh_token; obtain access token via refresh.
    if raw.get("refresh_token") and not raw.get("access_token") and not raw.get("token"):
        creds = Credentials(
            token=None,
            refresh_token=raw["refresh_token"],
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )
        creds.refresh(Request())
        return creds

    raw.setdefault("client_id", client_id)
    raw.setdefault("client_secret", client_secret)
    if "token" in raw and "access_token" not in raw:
        raw["access_token"] = raw["token"]
    creds = Credentials.from_authorized_user_info(raw, scopes=scopes)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as exc:
            if not creds.valid:
                raise RuntimeError(f"OAuth token refresh failed: {exc}") from exc
    if not creds or not creds.valid:
        raise RuntimeError(
            f"Invalid OAuth token at {token_file}; run scripts/auth_google_docs_mcp.ps1"
        )
    return creds


def _iter_text_runs(doc: dict[str, Any]):
    """Yield (start_index, content) for each text run in document order."""

    def walk(elements: list):
        for el in elements:
            if "paragraph" in el:
                for pe in el["paragraph"].get("elements", []):
                    if "textRun" in pe and "startIndex" in pe:
                        yield pe["startIndex"], pe["textRun"].get("content", "")
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        yield from walk(cell.get("content", []))

    yield from walk(doc.get("body", {}).get("content", []))


def _find_marker_indices(doc: dict[str, Any], start_marker: str, end_marker: str) -> tuple[int, int] | None:
    """Return API indices for content between markers (after START, before END)."""
    segments = list(_iter_text_runs(doc))
    if not segments:
        return None

    full_parts: list[str] = []
    index_map: list[int] = []
    for api_start, text in segments:
        for i, _ch in enumerate(text):
            full_parts.append(text[i])
            index_map.append(api_start + i)

    full = "".join(full_parts)
    s_pos = full.find(start_marker)
    e_pos = full.find(end_marker)
    if s_pos < 0 or e_pos < 0 or e_pos <= s_pos:
        return None

    content_start_plain = s_pos + len(start_marker)
    content_end_plain = e_pos
    if content_start_plain >= content_end_plain:
        # Empty block: insert at end marker position
        start_api = index_map[content_start_plain] if content_start_plain < len(index_map) else index_map[-1] + 1
        return start_api, start_api

    start_api = index_map[content_start_plain]
    end_api = index_map[content_end_plain]
    return start_api, end_api


def _document_end_index(doc: dict[str, Any]) -> int:
    content = doc.get("body", {}).get("content", [])
    if not content:
        return 1
    end = content[-1].get("endIndex", 1)
    return max(1, end - 1)


def push_markdown_to_doc(
    *,
    document_id: str,
    markdown: str,
    client_id: str,
    client_secret: str,
    token_file: Path,
) -> dict[str, Any]:
    try:
        from googleapiclient.discovery import build
    except ImportError as e:
        raise ImportError(
            "Install google-docs-sync extras: pip install -e '.[google-docs-sync]'"
        ) from e

    creds = _load_google_credentials(client_id, client_secret, token_file)
    service = build("docs", "v1", credentials=creds, cache_discovery=False)
    doc = service.documents().get(documentId=document_id).execute()

    insert_text = markdown.strip() + "\n"
    indices = _find_marker_indices(doc, MARKER_START, MARKER_END)
    requests: list[dict[str, Any]] = []
    bootstrapped = False

    if indices is None:
        # First run: append marker block at document end (no manual marker paste).
        end_idx = _document_end_index(doc)
        block = f"\n\n{MARKER_START}\n{insert_text}{MARKER_END}\n"
        requests.append({"insertText": {"location": {"index": end_idx}, "text": block}})
        bootstrapped = True
        start_idx, end_idx = end_idx, end_idx
    else:
        start_idx, end_idx = indices
        if end_idx > start_idx:
            requests.append(
                {"deleteContentRange": {"range": {"startIndex": start_idx, "endIndex": end_idx}}}
            )
        requests.append({"insertText": {"location": {"index": start_idx}, "text": insert_text}})

    service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
    return {
        "document_id": document_id,
        "start_index": start_idx,
        "end_index": end_idx,
        "chars_inserted": len(insert_text),
        "bootstrapped_markers": bootstrapped,
    }


def write_sync_report(repo: Path, report: dict[str, Any]) -> Path:
    cp = repo / "artifacts" / "control_plane"
    cp.mkdir(parents=True, exist_ok=True)
    path = cp / "msos_sync_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def run_sync(
    repo_root: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> int:
    repo = repo_root.resolve()
    env = _parse_env_mcp(repo)
    doc_id = env.get("MSOS_REPO_TRUTH_DOC_ID", "").strip()
    client_id = env.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = env.get("GOOGLE_CLIENT_SECRET", "").strip()
    token_file = _token_path()

    continuity_path = repo / "artifacts/control_plane/continuity_brief.json"
    closeout = None
    if continuity_path.is_file():
        try:
            closeout = json.loads(continuity_path.read_text(encoding="utf-8-sig")).get("closeout")
        except json.JSONDecodeError:
            closeout = None

    md, meta, snap_path = build_and_write(repo, closeout=closeout)

    base_report: dict[str, Any] = {
        "job": "sync_msos_repo_truth_v1",
        "passed": False,
        "skipped": False,
        "reason": None,
        "doc_id": doc_id or None,
        "head_sha": meta.head_sha,
        "generated_at": meta.generated_at,
        "snapshot_path": snap_path.as_posix(),
        "section15a_drift_warnings": meta.section15a_drift_warnings,
    }

    if dry_run:
        base_report["passed"] = True
        base_report["skipped"] = True
        base_report["reason"] = "dry_run"
        write_sync_report(repo, base_report)
        print(f"sync_msos_repo_truth: dry-run OK -> {snap_path}")
        return 0

    if not doc_id or not client_id or not client_secret or not token_file.is_file():
        base_report["passed"] = True
        base_report["skipped"] = True
        base_report["reason"] = "missing_env_or_token"
        write_sync_report(repo, base_report)
        print("sync_msos_repo_truth: skipped (missing .env.mcp, doc id, or OAuth token)")
        return 0

    try:
        push_result = push_markdown_to_doc(
            document_id=doc_id,
            markdown=md,
            client_id=client_id,
            client_secret=client_secret,
            token_file=token_file,
        )
        base_report["passed"] = True
        base_report["skipped"] = False
        base_report["push"] = push_result
        write_sync_report(repo, base_report)
        print(f"sync_msos_repo_truth: pushed to doc {doc_id}")
        return 0
    except ValueError as e:
        base_report["reason"] = str(e)
        write_sync_report(repo, base_report)
        print(f"sync_msos_repo_truth: {e}", file=sys.stderr)
        return 2 if not force else 1
    except ImportError as e:
        base_report["skipped"] = True
        base_report["reason"] = str(e)
        base_report["passed"] = True
        write_sync_report(repo, base_report)
        print(f"sync_msos_repo_truth: skipped ({e})")
        return 0
    except Exception as e:
        base_report["reason"] = str(e)
        write_sync_report(repo, base_report)
        print(f"sync_msos_repo_truth: failed ({e})", file=sys.stderr)
        return 1 if force else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync MSOS Repo Truth Google Doc from repo")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true", help="Build snapshot only; no Google API")
    parser.add_argument("--force", action="store_true", help="Non-zero exit on push failure")
    args = parser.parse_args(argv)
    return run_sync(args.repo_root.resolve(), dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
