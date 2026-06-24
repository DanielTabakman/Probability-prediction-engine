"""MSOS homepage UX — tutorial, research beta, simplified hero."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
COMPONENTS = MSOS_WEB / "src" / "components"
LIB = MSOS_WEB / "src" / "lib"


def test_hero_simplified_with_tutorial_and_research_modal() -> None:
    hero = (COMPONENTS / "HeroSection.tsx").read_text(encoding="utf-8")
    assert '"use client"' in hero
    assert "ResearchBetaModal" in hero
    assert "strategyLabTutorialHref" in hero
    assert "ActionLink" in hero
    assert "semantic-lock" not in hero
    assert "Open Command Center" not in hero


def test_public_nav_restart_tour() -> None:
    nav = (COMPONENTS / "PublicNav.tsx").read_text(encoding="utf-8")
    assert "Restart tour" in nav
    assert "clearPlatformTutorialComplete" in nav


def test_platform_tutorial_steps_and_storage() -> None:
    lib = (LIB / "platformTutorial.ts").read_text(encoding="utf-8")
    assert "PLATFORM_TUTORIAL_STEPS" in lib
    assert "lab-expiry" in lib
    assert "PlatformTutorial" in (COMPONENTS / "PlatformTutorial.tsx").read_text(encoding="utf-8")
    shell = (COMPONENTS / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    assert "PlatformTutorial" in shell
    assert "data-tour" in shell


def test_belief_bounds_copy_explains_limits() -> None:
    copy = (LIB / "beliefTuningCopy.ts").read_text(encoding="utf-8")
    fine = (COMPONENTS / "BeliefFineTuning.tsx").read_text(encoding="utf-8")
    builder = (COMPONENTS / "BeliefBuilder.tsx").read_text(encoding="utf-8")
    assert "BELIEF_TUNING_BOUNDS_NOTE" in copy
    assert "BELIEF_TAIL_LIMIT_NOTE" in copy
    assert "BELIEF_TUNING_BOUNDS_NOTE" in fine
    assert "BELIEF_TAIL_LIMIT_NOTE" in builder


def test_research_interest_api_route() -> None:
    route = (MSOS_WEB / "src" / "app" / "api" / "research-interest" / "route.ts").read_text(
        encoding="utf-8"
    )
    assert "research_beta_request" in route
    assert "appendWebFeedback" in route


def test_action_link_feedback_component() -> None:
    css = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert ".btn-pending" in css
    assert "btn-spin" in css
    assert "ActionLink" in (COMPONENTS / "ActionLink.tsx").read_text(encoding="utf-8")
