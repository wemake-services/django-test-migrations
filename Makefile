SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
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
