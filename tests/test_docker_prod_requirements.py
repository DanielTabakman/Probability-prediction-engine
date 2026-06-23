"""Production Docker image uses slim requirements (no playwright in image)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_uses_requirements_prod() -> None:
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    prod_lines = [
        line
        for line in (REPO_ROOT / "requirements-prod.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert "requirements-prod.txt" in dockerfile
    joined = "\n".join(prod_lines)
    assert "playwright" not in joined
    assert "pytest" not in joined
