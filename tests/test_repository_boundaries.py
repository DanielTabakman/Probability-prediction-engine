from pathlib import Path

import pytest

from scripts.check_repository_boundaries import find_violations


REPO = Path(__file__).resolve().parents[1]


def _minimal_repo(tmp_path: Path) -> Path:
    app_root = tmp_path / "apps/msos-web/src/app"
    app_root.mkdir(parents=True)
    return tmp_path


def test_current_repository_respects_product_boundary() -> None:
    assert find_violations(REPO) == []


def test_unknown_top_level_route_is_rejected(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    route = repo / "apps/msos-web/src/app/unrelated-game"
    route.mkdir()

    assert find_violations(repo) == [
        "unowned top-level MSOS route: apps/msos-web/src/app/unrelated-game"
    ]


@pytest.mark.parametrize(
    ("relative_path", "content", "expected_fragment"),
    [
        (
            "apps/msos-web/src/app/daniel/other-product/page.tsx",
            "export default function Page() { return null; }",
            "nested product code under /daniel",
        ),
        (
            "apps/msos-web/public/daniel/other-product.js",
            "console.log('other product');",
            "product asset stored under public/daniel",
        ),
        (
            "apps/msos-web/src/app/learn/page.tsx",
            "export default function Page() { return <iframe src='/other' />; }",
            "runtime iframe requires a repository-boundary decision",
        ),
        (
            "apps/msos-web/src/app/api/proxy/route.ts",
            'const upstream = "https://raw.githubusercontent.com/acme/game/main/app.js";',
            "remote application content is proxied at runtime",
        ),
    ],
)
def test_cross_product_hosting_patterns_are_rejected(
    tmp_path: Path,
    relative_path: str,
    content: str,
    expected_fragment: str,
) -> None:
    repo = _minimal_repo(tmp_path)
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    assert any(expected_fragment in violation for violation in find_violations(repo))
