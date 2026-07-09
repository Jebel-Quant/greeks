## .rhiza/make.d/custom-env.mk - Custom Environment Configuration
# This file example shows how to set variables for the project.

# Custom variables for this repository
PROJECT_NAME_EXTRA := Rhiza Platform
LOG_LEVEL ?= INFO

# Overriding core variables (be careful)
# VENV := .venv_custom

# Lock the test coverage gate at 100% (src/ is fully covered). The Rhiza default
# is 90% (`COVERAGE_FAIL_UNDER ?= 90` in test.mk); raising it here makes `make
# test` fail if coverage ever regresses.
COVERAGE_FAIL_UNDER := 100
