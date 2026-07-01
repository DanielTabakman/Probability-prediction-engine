"""Schedule recurring between-chapter housekeeping after product chapter closeouts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ppe_propagate_queue import (  # noqa: E402
    BACKLOG_REL,
    _is_side_channel,
    load_backlog,
    promote_first_blocked_with_plan,
    save_backlog,
)
from scripts.ppe_structural_health import STATE_REL  # noqa: E402

HOUSEKEEPING_CHAPTER_ID = "repo_between_chapter_housekeeping"
HOUSEKEEPING_PLAN_PATH = "docs/SOP/PHASE_PLANS/repo_between_chapter_housekeeping_relay.json"
BACKLOG_FLAG = "betweenChapterHousekeeping"
CHAPTERS_BETWEEN_THRESHOLD = 1


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def is_housekeeping_chapter(*, chapter_id: str = "", plan_path: str = "") -> bool:
    cid = str(chapter_id or "").strip()
    plan = _norm_plan(plan_path)
    if cid == HOUSEKEEPING_CHAPTER_ID:
        return True
    return plan == HOUSEKEEPING_PLAN_PATH


def _find_backlog_item(backlog: dict[str, Any]) -> dict[str, Any] | None:
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        if item.get(BACKLOG_FLAG) is True:
            return item
        if str(item.get("chapterId") or "").strip() == HOUSEKEEPING_CHAPTER_ID:
            return item
    return None


def load_state(repo: Path) -> dict[str, Any]:
    path = repo / STATE_REL
    if not path.is_file():
        return {"version": 1, "product_chapters_since_run": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "product_chapters_since_run": 0}
    if not isinstance(data, dict):
        return {"version": 1, "product_chapters_since_run": 0}
    data.setdefault("version", 1)
    data.setdefault("product_chapters_since_run", 0)
    return data


def save_state(repo: Path, state: dict[str, Any]) -> None:
    path = repo / STATE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _reset_queue_and_roadmap(repo: Path, plan_path: str, *, apply: bool) -> dict[str, Any]:
    out: dict[str, Any] = {"planPath": plan_path}
    if apply:
        from scripts.ppe_queue import upsert_queue_item

        ok, reason = upsert_queue_item(
            repo,
            plan_path=plan_path,
            status="READY",
            reason="between-chapter housekeeping scheduled after product closeout",
            workerMode="deterministic",
        )
        out["queue"] = {"ok": ok, "reason": reason}
    else:
        out["queue"] = {"dry_run": True, "status": "READY"}

    if apply:
        from scripts.ppe_roadmap import load_roadmap, roadmap_path, save_roadmap, _set_roadmap_status

        if roadmap_path(repo).is_file():
            roadmap = load_roadmap(repo)
            if _set_roadmap_status(roadmap, plan_path, "pending"):
                save_roadmap(repo, roadmap)
                out["roadmap"] = "pending"
            else:
                out["roadmap"] = "missing_row"
        else:
            out["roadmap"] = "no_roadmap_file"
    else:
        out["roadmap"] = {"dry_run": True, "status": "pending"}
    return out


def prepare_rerun(repo: Path, *, apply: bool) -> dict[str, Any]:
    """Reset backlog/queue/roadmap so the recurring housekeeping chapter can run again."""
    repo = repo.resolve()
    if not (repo / BACKLOG_REL).is_file():
        return {"prepared": False, "reason": "no backlog file"}

    backlog = load_backlog(repo)
    item = _find_backlog_item(backlog)
    if item is None:
        return {"prepared": False, "reason": "no betweenChapterHousekeeping backlog row"}

    plan_path = _norm_plan(str(item.get("planPath") or HOUSEKEEPING_PLAN_PATH))
    prev_status = str(item.get("status") or "").strip().lower()
    if apply:
        item["status"] = "blocked"
        save_backlog(repo, backlog)

    reset = _reset_queue_and_roadmap(repo, plan_path, apply=apply)
    return {
        "prepared": True,
        "chapterId": item.get("chapterId") or HOUSEKEEPING_CHAPTER_ID,
        "planPath": plan_path,
        "previous_backlog_status": prev_status,
        "backlog_status": "blocked",
        **reset,
    }


def schedule_after_product_closeout(
    repo: Path,
    *,
    closed_chapter_id: str = "",
    closed_plan_path: str = "",
    apply: bool = True,
) -> dict[str, Any]:
    """After a product chapter closeout, queue between-chapter housekeeping when due."""
    repo = repo.resolve()
    if is_housekeeping_chapter(chapter_id=closed_chapter_id, plan_path=closed_plan_path):
        return {"scheduled": False, "reason": "housekeeping chapter closeout — skip self-schedule"}

    backlog = load_backlog(repo) if (repo / BACKLOG_REL).is_file() else None
    item = _find_backlog_item(backlog) if backlog else None
    if item is None:
        return {"scheduled": False, "reason": "no betweenChapterHousekeeping backlog row"}

    state = load_state(repo)
    count = int(state.get("product_chapters_since_run") or 0) + 1
    state["product_chapters_since_run"] = count
    state["last_product_closeout_at"] = _utc_now()
    state["last_product_closeout_chapter"] = str(closed_chapter_id or closed_plan_path).strip()
    state["last_product_closeout_plan"] = _norm_plan(closed_plan_path)

    if count < CHAPTERS_BETWEEN_THRESHOLD:
        if apply:
            save_state(repo, state)
        return {
            "scheduled": False,
            "reason": f"threshold not reached ({count}/{CHAPTERS_BETWEEN_THRESHOLD})",
            "product_chapters_since_run": count,
        }

    prep = prepare_rerun(repo, apply=apply)
    if not prep.get("prepared"):
        if apply:
            save_state(repo, state)
        return {"scheduled": False, "reason": prep.get("reason"), "product_chapters_since_run": count}

    state["product_chapters_since_run"] = 0
    state["last_scheduled_at"] = _utc_now()
    state["last_scheduled_after"] = state.get("last_product_closeout_chapter")
    if apply:
        save_state(repo, state)

    promote: dict[str, Any] = {}
    if apply and _is_side_channel(item):
        promote = promote_first_blocked_with_plan(repo, apply=True)
    elif not apply:
        promote = {"dry_run": True}

    return {
        "scheduled": True,
        "product_chapters_since_run": 0,
        "prepare": prep,
        "promote": promote,
        "sideChannel": bool(_is_side_channel(item)),
    }


def note_housekeeping_completed(repo: Path, *, apply: bool = True) -> dict[str, Any]:
    """Record successful housekeeping run (called after recurring chapter closeout)."""
    state = load_state(repo)
    state["last_completed_at"] = _utc_now()
    state["product_chapters_since_run"] = 0
    if apply:
        save_state(repo, state)
    return {"noted": True, "state": state}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Between-chapter housekeeping scheduler")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--closed-chapter-id", type=str, default="")
    ap.add_argument("--closed-plan-path", type=str, default="")
    ap.add_argument("--completed", action="store_true", help="Mark housekeeping chapter completed")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    apply = not args.dry_run

    if args.completed:
        out = note_housekeeping_completed(repo, apply=apply)
    elif args.prepare_only:
        out = prepare_rerun(repo, apply=apply)
    else:
        out = schedule_after_product_closeout(
            repo,
            closed_chapter_id=args.closed_chapter_id,
            closed_plan_path=args.closed_plan_path,
            apply=apply,
        )

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
