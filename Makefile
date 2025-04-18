SHELL:=/usr/bin/env bash

.PHONY: format
format:
	poetry run ruff format
	poetry run ruff check

.PHONY: lint
lint:
	poetry run ruff check --exit-non-zero-on-fix --diff
	poetry run ruff format --check --diff
	poetry run mypy django_test_migrations
	poetry run flake8 .

.PHONY: unit
unit:
	# We need one more test run to make sure that `--nomigrations` work:
	poetry run pytest -p no:cov -o addopts="" --nomigrations
	poetry run pytest

.PHONY: package
package:
	poetry check
	poetry run pip check

.PHONY: test
test: lint unit package
