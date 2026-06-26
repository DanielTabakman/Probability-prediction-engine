"""MSOS display currency — multi-fiat display-only layer (msos-shell)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO / "apps" / "msos-web"


def test_display_currency_supports_multi_fiat() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "displayCurrency.ts").read_text(encoding="utf-8")
    assert "EUR" in lib
    assert "GBP" in lib
    assert "AUD" in lib
    assert "CHF" in lib
    assert "formatAxisAmount" in lib
    assert "displayCurrencyDisclaimer" in lib
    assert "parseDisplayCurrencyFromCookie" in lib
    assert "fxPerUsd" in lib


def test_chart_axis_respects_display_currency() -> None:
    axis = (MSOS_WEB / "src" / "lib" / "chartAxisDisplay.ts").read_text(encoding="utf-8")
    chart = (MSOS_WEB / "src" / "components" / "ExpressionPayoffChart.tsx").read_text(encoding="utf-8")
    dist = (MSOS_WEB / "src" / "components" / "LabeledDistributionChart.tsx").read_text(encoding="utf-8")
    assert "formatAxisPrice(value, currency)" in axis or "formatAxisAmount" in axis
    assert "formatAxisPrice(price, currency)" in chart
    assert "formatAxisPrice(price, currency)" in dist


def test_monitor_ssr_reads_currency_cookie() -> None:
    monitor_page = (MSOS_WEB / "src" / "app" / "monitor" / "page.tsx").read_text(encoding="utf-8")
    server = (MSOS_WEB / "src" / "lib" / "displayCurrencyServer.ts").read_text(encoding="utf-8")
    assert "resolveDisplayCurrency" in monitor_page
    assert "DISPLAY_CURRENCY_COOKIE" in server


def test_paper_trade_detail_uses_server_display_currency() -> None:
    detail = (MSOS_WEB / "src" / "components" / "PaperTradeDetailContent.tsx").read_text(encoding="utf-8")
    page = (MSOS_WEB / "src" / "app" / "monitor" / "paper" / "[id]" / "page.tsx").read_text(
        encoding="utf-8"
    )
    assert "use client" not in detail
    assert "displayCurrency" in detail
    assert "formatMoney" in detail
    assert "resolveDisplayCurrency" in page


def test_belief_expiry_picker_enabled() -> None:
    panel = (MSOS_WEB / "src" / "components" / "StrategyLabInteractivePanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "hideInlineExpiryPicker={false}" in panel


def test_lab_setup_row_has_expiry_and_currency() -> None:
    setup = (MSOS_WEB / "src" / "components" / "LabSetupRow.tsx").read_text(encoding="utf-8")
    strip = (MSOS_WEB / "src" / "components" / "ExpiryMarketContextStrip.tsx").read_text(
        encoding="utf-8"
    )
    assert "LabSetupRow" in strip
    assert "Display currency" in setup
    assert "ExpiryPicker" in setup


def test_monitor_mark_line_is_client_safe() -> None:
    mark = (MSOS_WEB / "src" / "lib" / "monitorMarkLine.ts").read_text(encoding="utf-8")
    watch = (MSOS_WEB / "src" / "components" / "MonitorWatchList.tsx").read_text(encoding="utf-8")
    assert "formatMarkLine" in mark
    assert 'import { formatMarkLine } from "@/lib/monitorMarkLine"' in watch
    assert 'import type { MonitorWatchPanel } from "@/lib/monitorHistoryFeed"' in watch


def test_deploy_docs_list_fx_env_vars() -> None:
    doc = (REPO / "docs" / "DEPLOY" / "MSOS_WEB_V1.md").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_MSOS_EUR_PER_USD" in doc
    assert "NEXT_PUBLIC_MSOS_GBP_PER_USD" in doc
