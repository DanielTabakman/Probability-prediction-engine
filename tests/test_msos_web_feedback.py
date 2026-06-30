"""Export MSOS web feedback JSONL for operator review."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_feedback_api_route_exists() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "feedback" / "route.ts"
    lib = MSOS_WEB / "src" / "lib" / "webFeedback.ts"
    assert route.is_file()
    assert lib.is_file()
    text = route.read_text(encoding="utf-8")
    assert "appendWebFeedback" in text
    assert "feedbackForm" in text


def test_public_feedback_page_exists() -> None:
    page = MSOS_WEB / "src" / "app" / "feedback" / "page.tsx"
    form = MSOS_WEB / "src" / "components" / "WebFeedbackForm.tsx"
    assert page.is_file()
    assert form.is_file()
    assert "public_feedback" in page.read_text(encoding="utf-8")


def test_strategy_lab_feedback_strip_wired() -> None:
    shell = MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx"
    strip = MSOS_WEB / "src" / "components" / "StrategyLabFeedbackStrip.tsx"
    assert strip.is_file()
    text = shell.read_text(encoding="utf-8")
    assert "StrategyLabFeedbackStrip" in text


def test_learn_debrief_submits_feedback() -> None:
    debrief = MSOS_WEB / "src" / "components" / "DemoSessionDebrief.tsx"
    text = debrief.read_text(encoding="utf-8")
    assert "/api/feedback" in text
    assert "learn_debrief" in text
    assert "Submit feedback" in text


def test_session_json_includes_survey() -> None:
    raw = (MSOS_WEB / "public" / "session.json").read_text(encoding="utf-8")
    data = json.loads(raw)
    survey = data.get("survey")
    assert isinstance(survey, dict)
    cats = survey.get("confusionCategories")
    assert isinstance(cats, list) and len(cats) >= 5


def test_session_html_references_survey_submit() -> None:
    html = (MSOS_WEB / "public" / "session.html").read_text(encoding="utf-8")
    assert "renderSurvey" in html
    assert "/api/feedback" in html
    assert "submit-survey" in html


def test_msos_web_compose_feedback_volume() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "msos_web_data" in compose
    assert "PPE_WEB_FEEDBACK_DIR" in compose


def test_feedback_form_categories_shared() -> None:
    lib = MSOS_WEB / "src" / "lib" / "feedbackForm.ts"
    assert lib.is_file()
    text = lib.read_text(encoding="utf-8")
    assert "CONFUSION_CATEGORIES" in text
    assert "market-read confusion" in text
