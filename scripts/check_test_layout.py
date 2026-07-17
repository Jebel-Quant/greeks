"""Check that test files mirror source modules.

For every Python module under src/, there must be a corresponding test file
under tests/ with the same relative path (module ``src/greeks/foo.py``
maps to test ``tests/greeks/test_foo.py``).  Conversely, every
``tests/**/test_*.py`` file must map back to a real source module — with
the exception of files whose names indicate cross-cutting concerns
(e.g. ``test_properties.py``).

Exit codes:
    0  All checks pass.
    1  One or more checks failed.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent
SRC_ROOT = ROOT / "src"
TEST_ROOT = ROOT / "tests"

# Modules whose names are conventionally skipped by the checker — they test
# cross-cutting properties rather than mapping 1-to-1 to a source file.
# ``test_properties.py`` uses Hypothesis to assert invariants that span the
# whole public API and has no corresponding ``properties.py`` source module.
ALLOWED_ORPHANS: frozenset[str] = frozenset({"properties"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _source_modules() -> list[Path]:
    """Return every non-``__init__`` Python module under *SRC_ROOT*."""
    return [p for p in SRC_ROOT.rglob("*.py") if p.name != "__init__.py" and not p.name.startswith("_")]


def _expected_test_path(src: Path) -> Path:
    """Return the expected test file for *src*.

    ``src/greeks/black_scholes.py`` → ``tests/greeks/test_black_scholes.py``
    """
    relative = src.relative_to(SRC_ROOT)
    test_name = f"test_{relative.name}"
    return TEST_ROOT / relative.parent / test_name


def _test_files() -> list[Path]:
    """Return every ``test_*.py`` file under *TEST_ROOT*."""
    return list(TEST_ROOT.rglob("test_*.py"))


def _source_module_for_test(test: Path) -> Path:
    """Return the expected source module for *test* (inverse of :func:`_expected_test_path`)."""
    relative = test.relative_to(TEST_ROOT)
    src_name = relative.name[len("test_") :]  # strip leading "test_"
    return SRC_ROOT / relative.parent / src_name


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_missing_tests(errors: list[str]) -> None:
    """Every source module must have a mirrored test file."""
    for src in sorted(_source_modules()):
        expected = _expected_test_path(src)
        if not expected.exists():
            errors.append(f"✗ missing test file {expected.relative_to(ROOT)} for source module {src.relative_to(ROOT)}")
        else:
            print(f"✓ {expected.relative_to(ROOT)}")


def check_orphan_tests(errors: list[str]) -> None:
    """Every test file must map back to a real source module."""
    for test in sorted(_test_files()):
        stem = test.stem  # e.g. "test_black_scholes"
        module_name = stem[len("test_") :]  # e.g. "black_scholes"
        if module_name in ALLOWED_ORPHANS:
            print(f"✓ {test.relative_to(ROOT)} (allowed cross-cutting test)")
            continue
        expected_src = _source_module_for_test(test)
        if not expected_src.exists():
            errors.append(
                f"✗ orphan test file {test.relative_to(ROOT)} (no source module {expected_src.relative_to(ROOT)})"
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Run all checks and return an exit code."""
    errors: list[str] = []

    check_missing_tests(errors)
    check_orphan_tests(errors)

    if errors:
        print("\nTest-layout parity FAILED:\n")
        for err in errors:
            print(f"  {err}")
        print()
        return 1

    print("\nTest-layout parity OK.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
