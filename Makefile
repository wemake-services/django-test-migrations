SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run mypy django_test_migrations
	poetry run flake8 .

.PHONY: unit
unit:
	# We need one more test run to make sure that `--nomigrations` work:
	poetry run pytest -p no:cov -o addopts="" --nomigrations
	# Real `pytest` execution:
	poetry run pytest

.PHONY: package
package:
	poetry check
	poetry run pip check

.PHONY: safety
safety:
	# Is not run by default, is a separate command.
	poetry run safety check --full-report

.PHONY: test
test: lint unit package
