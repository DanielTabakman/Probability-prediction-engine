"""MSOS web feedback API and session notebook survey wiring."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_feedback_api_route_exists() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "feedback" / "route.ts"
    lib = MSOS_WEB / "src" / "lib" / "webFeedback.ts"
    assert route.is_file()
    assert lib.is_file()
    text = route.read_text(encoding="utf-8")
    assert "appendWebFeedback" in text


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
