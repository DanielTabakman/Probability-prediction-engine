"""MSOS web feedback, operator inbox, and public copy gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_feedback_api_route_exists() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "feedback" / "route.ts"
    assert route.is_file()
    text = route.read_text(encoding="utf-8")
    assert "feedbackForm" in text


def test_public_feedback_page_exists() -> None:
    page = MSOS_WEB / "src" / "app" / "feedback" / "page.tsx"
    form = MSOS_WEB / "src" / "components" / "WebFeedbackForm.tsx"
    assert page.is_file() and form.is_file()
    assert "public_feedback" in page.read_text(encoding="utf-8")


def test_operator_feedback_inbox_exists() -> None:
    page = MSOS_WEB / "src" / "app" / "operator" / "feedback" / "page.tsx"
    auth = MSOS_WEB / "src" / "lib" / "operatorAuth.ts"
    assert page.is_file() and auth.is_file()
    assert "readWebFeedbackRecords" in page.read_text(encoding="utf-8")


def test_strategy_lab_feedback_strip_wired() -> None:
    shell = MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx"
    assert "StrategyLabFeedbackStrip" in shell.read_text(encoding="utf-8")


def test_learn_debrief_submits_feedback() -> None:
    debrief = MSOS_WEB / "src" / "components" / "DemoSessionDebrief.tsx"
    text = debrief.read_text(encoding="utf-8")
    assert "/api/feedback" in text and "learn_debrief" in text


def test_session_json_includes_survey() -> None:
    raw = (MSOS_WEB / "public" / "session.json").read_text(encoding="utf-8")
    data = json.loads(raw)
    assert isinstance(data.get("survey"), dict)


def test_msos_web_compose_feedback_volume() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "PPE_WEB_FEEDBACK_DIR" in compose
