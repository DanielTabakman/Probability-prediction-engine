"""MSOS P4 Strategy Lab scaffold witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_strategy_lab_route_and_shell() -> None:
    page = MSOS_WEB / "src" / "app" / "strategy-lab" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "AppShell" in text
    assert "StrategyLabContent" in text
    assert 'activeNavId="strategy-lab"' in text


def test_strategy_lab_hierarchy_and_embed_boundary() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "Strategy Lab / PPE / Distribution summary" in content
    assert "Strategy Lab — research demo" in content
    assert "Live via PPE when embed wired" in content
    assert "Distribution summary (live PPE)" in content
    assert "PpeEmbedBoundary" in content
    assert "no live order transmitted" in content

    embed = (MSOS_WEB / "src" / "components" / "PpeEmbedBoundary.tsx").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_PPE_EMBED_URL" in embed
    assert "iframe" in embed
    assert "degraded" in embed.lower() or "Embed pending" in embed
    assert "distribution-summary" in embed
    assert "Live via PPE" in embed


def test_strategy_lab_fixtures_honest_lens_labels() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "strategyLabFixtures.ts").read_text(encoding="utf-8")
    assert "LIVE" in fixtures
    assert "Planned" in fixtures
    assert "Soon" in fixtures
    assert "BTC / Options" in fixtures


def test_nav_enables_strategy_lab() -> None:
    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'id: "strategy-lab"' in nav
    assert 'href: "/strategy-lab"' in nav
    assert "disabled: true" not in nav.split("strategy-lab")[1].split("theses")[0]

    cc = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert 'href="/strategy-lab"' in cc
