"""MSOS web product usage wiring (Q-009 v0)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_usage_api_route_exists() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "usage" / "event" / "route.ts"
    lib = MSOS_WEB / "src" / "lib" / "webProductUsage.ts"
    assert route.is_file()
    assert lib.is_file()
    text = route.read_text(encoding="utf-8")
    assert "appendProductUsageEvent" in text


def test_product_usage_beacon_wired_in_layout() -> None:
    layout = (MSOS_WEB / "src" / "app" / "layout.tsx").read_text(encoding="utf-8")
    assert "ProductUsageBeacon" in layout


def test_product_usage_beacon_session_start() -> None:
    beacon = (MSOS_WEB / "src" / "components" / "ProductUsageBeacon.tsx").read_text(encoding="utf-8")
    assert "session_start" in beacon
    assert "sessionStorage" in beacon


def test_distribution_export_client_link() -> None:
    link = MSOS_WEB / "src" / "components" / "DistributionExportLink.tsx"
    shell = MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx"
    assert link.is_file()
    assert "distribution_export_click" in link.read_text(encoding="utf-8")
    assert "DistributionExportLink" in shell.read_text(encoding="utf-8")


def test_strategy_lab_logs_lab_view() -> None:
    shell = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    assert "logProductUsage" in shell
    assert "lab_view" in shell


def test_msos_web_compose_product_usage_volume() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "PPE_PRODUCT_USAGE_DIR" in compose


def test_msos_web_docker_entrypoint_chowns_product_usage_volume() -> None:
    dockerfile = (MSOS_WEB / "Dockerfile").read_text(encoding="utf-8")
    entrypoint = (MSOS_WEB / "docker-entrypoint.sh").read_text(encoding="utf-8")
    assert "su-exec" in dockerfile
    assert "docker-entrypoint.sh" in dockerfile
    assert "PPE_PRODUCT_USAGE_DIR" in entrypoint
    assert "chown -R nextjs:nodejs /data" in entrypoint


def test_review_route_logs_usage() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "snapshots" / "[id]" / "review" / "route.ts"
    text = route.read_text(encoding="utf-8")
    assert "review_submit" in text
    assert "appendProductUsageEvent" in text


def test_distribution_export_logs_usage() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "ppe-display-api" / "distribution-export" / "route.ts"
    text = route.read_text(encoding="utf-8")
    assert "distribution_export" in text
    assert "appendProductUsageEvent" in text


def test_feedback_route_logs_usage() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "feedback" / "route.ts"
    text = route.read_text(encoding="utf-8")
    assert "feedback_submit" in text
    assert "appendProductUsageEvent" in text
