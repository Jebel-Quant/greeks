# CLAUDE.md

Guidance for working in this repository.

## What this is

`greeks` — option pricing and the Greeks under Black-Scholes, part of the
[jebel-quant](https://github.com/jebel-quant) ecosystem. Deliberately small:
closed-form formulas over floats, with `scipy` and `numpy` as the only runtime
dependencies. No parser, no I/O, no untrusted input.

The whole library is `src/greeks/black_scholes.py`, re-exported flat from
`greeks/__init__.py`:

```text
OptionType, price, delta, gamma, vega, theta, rho
```

`__init__.py` carries an explicit `__all__`. A new user-facing symbol goes in
`black_scholes.py`, gets re-exported there, and is added to `__all__` — keeping
the public API flat is the convention, not an accident.

## Ownership: locally owned vs Rhiza-managed

This repo syncs its dev infrastructure from the
[`jebel-quant/rhiza`](https://github.com/jebel-quant/rhiza) template. The pinned
version lives in `.rhiza/template.yml` (`ref:`), and `/rhiza:update` re-applies
the template. **The authoritative, machine-generated list of synced files is the
`files:` block of `.rhiza/template.lock`** — when in doubt, consult it. The split
below summarises it.

### Locally owned — edit these freely

- `src/` — the library source
- `tests/` — the test suite
- `pyproject.toml` — project metadata, dependency groups, tool config, and the
  `[tool.rhiza-task]` table that configures the gates
- `README.md`, `CHANGELOG.md`, `mkdocs.yml`, `CLAUDE.md`
- `.lycheeignore` — the link-checker exclusions
- `.rhiza/template.yml` — the template pin and the `profiles:`/`templates:`
  selection. The one file under `.rhiza/` this repo owns.
- `local.mk` — repo-specific make targets. The `Makefile` `-include`s it, and the
  template deliberately does not ignore it.

### Rhiza-managed — do NOT edit in place; fix upstream

These are overwritten by the next sync. To change one, open a PR against
`jebel-quant/rhiza` (or exclude the path in `.rhiza/template.yml`), then re-sync:

- `.github/workflows/rhiza_*.yml` — all CI/CD workflows
- `.github/` scaffolding — `dependabot.yml`, `release.yml`, rulesets,
  `secret_scanning.yml`. `CONFIG.md` is excluded in `template.yml` rather than
  synced.
- `Makefile` — a 71-line shim that pins `RHIZA_TASK` and forwards every unmatched
  target to that CLI. Nothing goes below it; the next sync overwrites whatever was
  appended. Repo targets belong in `local.mk`.
- `.pre-commit-config.yaml`, `ruff.toml`, `pytest.ini`, `.bandit`,
  `.editorconfig`, `.python-version`, `cliff.toml` — tooling config
- `LICENSE`, `SECURITY.md`, and the synced `docs/` pages

`SECURITY.md` in particular is synced here: an edit to it is drift the next sync
reverts, and the `check-managed-files` pre-commit hook refuses the commit.

## Quality gates

Since rhiza v1.4 the gates are tasks in the pinned `rhiza-task` CLI rather than
synced make fragments. Run them as bare `make <target>` (the shim forwards to
`uvx rhiza-task <task>`) — never call `.venv/bin/...` directly. `make help` lists
every task the pinned CLI knows, plus anything `local.mk` adds.

- `make install` — create the venv and sync dependencies
- `make fmt` — the pre-commit hooks over all files
- `make typecheck` — `ty` **and** `mypy`, because `[tool.rhiza-task]` sets
  `typechecker = "both"`
- `make test` — the full pytest suite with the coverage gate
- `make coverage` — coverage measurement into `_tests/coverage.xml`
- `make docs-coverage` — interrogate docstring coverage
- `make deps` — deptry unused/missing dependency analysis
- `make security` — the bandit scan
- `make license` — fail on GPL/LGPL/AGPL
- `make rhiza-test` — the rhiza repository checks, from `pytest-rhiza==0.2.1`
- `make book` / `make serve` — build the docs book, and serve it on port 8000
- `make all` — the gate set CI runs

Do not reach for `make mutation`. The task still exists in the CLI, but rhiza
v1.5.0 stopped offering mutation testing (Jebel-Quant/rhiza#1492) and the recipe
drives a mutmut 2.x CLI that mutmut 3 removed.

## Conventions

- **Coverage must stay at 100%.** `[tool.rhiza-task]` sets
  `coverage-fail-under = 100`, above rhiza-task's default of 90. Over two small
  modules that is a reachable bar, and it is the reason this repo needs neither
  fuzzing nor mutation testing to answer the assertion-strength question.
- `mkdocs-extra-packages = ["mkdocstrings[python]", "."]` in `[tool.rhiza-task]`
  — the API pages are generated from docstrings, so the book build installs the
  package itself. A docstring change shows up in the book.
- Every public symbol needs a docstring; docstring coverage must stay at 100%.
- The per-test timeout is 60s (`pytest-timeout`).
- Three markers are declared: `stress`, `property`, `kaleido`. Use them rather
  than inventing new ones.
- `.lycheeignore` currently excludes `https://jebel-quant.github.io/greeks`
  because GitHub Pages is not enabled yet. Remove that line once the book
  workflow deploys successfully — it is a temporary exclusion, not a permanent one.

## Test layout

Two files, mirroring the source:

- `tests/greeks/test_black_scholes.py` — the library. Everything the package does
  is tested here, which is what makes the 100% gate practical.
- `tests/test_rhiza_packaging.py` — repo-level packaging invariants.

Property-based tests belong under the `property` marker. Because the functions
are closed-form, prefer pinning against analytic identities (put-call parity,
Greeks as derivatives of `price`) over golden numbers — an identity keeps holding
when a formula is refactored.
