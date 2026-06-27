# Acceptance test naming v1

**Purpose:** Link phase-plan `acceptance[].verify` to pytest nodes.

## Convention (new tests)

- `test_<SliceId_with_underscores>_<behavior>`
- or `test_<area>_<acceptance_id>`

## verify field

Prefer full node: `tests/test_foo.py::test_bar`

`python -m scripts.validate_phase_plans --check-test-names` warns on missing paths (advisory).
