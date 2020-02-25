# -*- coding: utf-8 -*-

import pytest
from django.core.checks import WARNING

from django_test_migrations.autonames import CHECK_NAME, check_migration_names


@pytest.mark.django_db
def test_autonames():
    """Here we check that bad migrations do produce warnings."""
    warnings = check_migration_names()

    assert len(warnings) == 1
    assert warnings[0].level == WARNING
    assert warnings[0].id.startswith(CHECK_NAME)
    assert 'main_app.0004_auto_20191119_2125' in warnings[0].msg


@pytest.mark.django_db
def test_autonames_with_ignore(ignore_migration):
    """Here we check that some migrations can be ignored."""
    warnings = check_migration_names()

    assert not warnings
