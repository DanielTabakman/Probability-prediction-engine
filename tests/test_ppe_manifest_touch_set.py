"""Phase plan validation requires touchSet on PRODUCT-PLANE slices."""

from __future__ import annotations

from scripts.ppe_manifest import validate_phase_plan


def test_product_slice_requires_touch_set():
    plan = {
        "slices": [
            {
                "sliceId": "P1",
                "declaredPlane": "PRODUCT-PLANE",
            },
            {
                "sliceId": "C1",
                "declaredPlane": "CONTROL-PLANE",
                "closeout": {"chapterId": "x"},
            },
        ]
    }
    errors = validate_phase_plan(plan)
    assert any("touchSet" in e for e in errors)


def test_product_slice_with_touch_set_ok():
    plan = {
        "slices": [
            {
                "sliceId": "P1",
                "declaredPlane": "PRODUCT-PLANE",
                "touchSet": ["src/viz/app_panels.py"],
            },
            {
                "sliceId": "C1",
                "declaredPlane": "CONTROL-PLANE",
                "closeout": {"chapterId": "x"},
            },
        ]
    }
    errors = validate_phase_plan(plan)
    assert not any("touchSet" in e for e in errors)
