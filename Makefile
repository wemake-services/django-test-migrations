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
	# vulnerabilities 40637, 49733, 50454 are ignored because we need to run
	# tests against vulnerable `Django<3.2.15`
	poetry run safety check \
		--full-report \
		--ignore 40637 \
		--ignore 49733 \
		--ignore 50454

.PHONY: test
test: lint unit package
