SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	mypy django_test_migrations
	flake8 .

.PHONY: unit
unit:
	# We need one more test run to make sure that `--nomigrations` work:
	pytest --nomigrations --cov-fail-under=0
	# Real `pytest` execution:
	pytest

.PHONY: package
package:
	poetry check
	pip check
	safety check --bare --full-report

.PHONY: test
test: lint unit package
