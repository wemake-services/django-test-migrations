SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run mypy django_test_migrations
	poetry run flake8 .

.PHONY: unit
unit:
	# We need one more test run to make sure that `--nomigrations` work:
	poetry run pytest --nomigrations --cov-fail-under=0
	# Real `pytest` execution:
	poetry run pytest

.PHONY: package
package:
	poetry check
	poetry run pip check
	poetry run safety check --bare --full-report

.PHONY: test
test: lint unit package
