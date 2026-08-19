## Makefile (repo-owned)
# Keep this file small. It can be edited without breaking template sync.

# Override template default: `make book` builds via `uvx ... zensical build`, which
# runs in an isolated environment where neither this project nor mkdocstrings is
# importable. docs/api.md uses a `::: greeks.black_scholes` directive, so the build
# needs both — without them zensical fails with either "Could not collect
# 'greeks.black_scholes'" (package missing) or "mkdocstrings plugin is enabled, but
# mkdocstrings is not installed" (pulling in `.` changes what zensical's own
# resolution provides). Passed to `uvx` ahead of the zensical spec by
# .rhiza/make.d/book.mk. Kept here, not in .rhiza/.env, because this file is
# repo-owned and a template sync cannot overwrite it.
MKDOCS_EXTRA_PACKAGES = --with . --with 'mkdocstrings[python]'

# Always include the Rhiza API (template-managed)
include .rhiza/rhiza.mk

# Optional: developer-local extensions (not committed)
-include local.mk
