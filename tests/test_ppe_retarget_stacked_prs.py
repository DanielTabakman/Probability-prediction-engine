"""Tests for stacked PR retarget helper."""

from __future__ import annotations

from pathlib import Path

from scripts.retarget_stacked_prs import (
    retarget_children_of_branch,
    retarget_pull_request,
    scan_and_retarget_stacked_prs,
)


def test_retarget_children_dry_run() -> None:
    repo = Path(".")

    def _children(_repo: Path, base: str) -> list[dict]:
        assert base == "build/auto/parent-slice"
        return [{"number": 42, "isDraft": False, "headRefName": "build/auto/child-slice"}]

    report = retarget_children_of_branch(
        repo,
        "build/auto/parent-slice",
        merged_pr=7,
        dry_run=True,
        list_children=_children,
    )
    assert report["ok"] is True
    assert report["parent_branch"] == "build/auto/parent-slice"
    assert len(report["retargeted"]) == 1
    assert report["retargeted"][0]["action"] == "would_retarget"


def test_retarget_children_skips_draft() -> None:
    repo = Path(".")

    def _children(_repo: Path, _base: str) -> list[dict]:
        return [{"number": 99, "isDraft": True}]

    report = retarget_children_of_branch(
        repo,
        "build/auto/parent",
        dry_run=True,
        list_children=_children,
    )
    assert report["ok"] is True
    assert report["retargeted"][0].get("reason") == "draft"


def test_retarget_children_skips_main_parent() -> None:
    report = retarget_children_of_branch(Path("."), "main", dry_run=True)
    assert report.get("skipped") is True


def test_scan_retarget_no_gh(monkeypatch) -> None:
    monkeypatch.setattr("scripts.retarget_stacked_prs._gh_available", lambda: False)
    report = scan_and_retarget_stacked_prs(Path("."))
    assert report["ok"] is False
    assert report["error"] == "gh not available"


def test_scan_retarget_when_parent_merged(monkeypatch) -> None:
    repo = Path(".")

    def _open(_repo: Path, *, main: str = "main") -> list[dict]:
        return [{"number": 50, "baseRefName": "build/auto/parent", "isDraft": False}]

    def _merged(_repo: Path, parent: str, *, main: str = "main"):
        if parent == "build/auto/parent":
            return {"number": 10, "title": "parent slice"}
        return None

    monkeypatch.setattr("scripts.retarget_stacked_prs._gh_available", lambda: True)
    monkeypatch.setattr("scripts.retarget_stacked_prs.list_open_prs_not_on_main", _open)
    monkeypatch.setattr("scripts.retarget_stacked_prs.find_merged_pr_to_main", _merged)
    monkeypatch.setattr(
        "scripts.retarget_stacked_prs.retarget_children_of_branch",
        lambda _repo, parent, **kwargs: {
            "action": "retarget_children",
            "ok": True,
            "parent_branch": parent,
            "retargeted": [{"number": 50, "ok": True, "dry_run": kwargs.get("dry_run")}],
        },
    )

    report = scan_and_retarget_stacked_prs(repo, dry_run=True)
    assert report["ok"] is True
    assert report["scanned_parents"] == 1
    assert report["results"][0]["parent_branch"] == "build/auto/parent"


def test_retarget_pull_request_dry_run() -> None:
    report = retarget_pull_request(Path("."), 1, parent_branch="build/auto/x", merged_pr=2, dry_run=True)
    assert report["ok"] is True
    assert report["action"] == "would_retarget"
