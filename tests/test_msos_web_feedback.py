"""MSOS web feedback capture witness."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_msos_web_feedback_routes_and_components() -> None:
    assert (MSOS_WEB / "src" / "app" / "feedback" / "page.tsx").is_file()
    assert (MSOS_WEB / "src" / "app" / "operator" / "feedback" / "page.tsx").is_file()
    assert (MSOS_WEB / "src" / "app" / "api" / "feedback" / "route.ts").is_file()
    assert (MSOS_WEB / "src" / "components" / "FeedbackForm.tsx").is_file()
    form = (MSOS_WEB / "src" / "components" / "FeedbackForm.tsx").read_text(encoding="utf-8")
    assert "understood" in form
    assert "would_return" in form
    assert "trader_profile" in form
    assert "/api/feedback" in form
    lab = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "FeedbackForm" in lab


def test_msos_web_feedback_docker_volume() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "PPE_WEB_FEEDBACK_DIR" in compose
    assert "ppe_web_feedback:" in compose


def test_export_web_feedback_reads_jsonl(tmp_path: Path, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    path = data_dir / "ppe_web_feedback.jsonl"
    row = {
        "id": "abc",
        "created_at_utc": "2026-06-13T12:00:00Z",
        "understood": "yes",
        "would_return": "yes",
        "trader_profile": "crypto_vol",
        "note": "SOL please",
        "source": "msos_web",
        "page_path": "/strategy-lab",
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setenv("PPE_WEB_FEEDBACK_DIR", str(data_dir))

    from scripts.ppe_export_web_feedback import load_entries

    loaded = load_entries(path)
    assert len(loaded) == 1
    assert loaded[0]["trader_profile"] == "crypto_vol"
