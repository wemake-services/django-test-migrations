# -*- coding: utf-8 -*-

import pytest
from django.core.checks import WARNING

from django_test_migrations.autonames import CHECK_NAME, check_migration_names


@pytest.mark.django_db
def test_autonames():
    """Here we check that bad migrations do produce warnings."""
    warnings = check_migration_names()
    warnings_msgs = [i.msg for i in warnings]

    assert len(warnings) == 2

    assert warnings[0].level == WARNING
    assert warnings[0].id.startswith(CHECK_NAME)
    assert ('Migration main_app.0004_auto_20191119_2125 has an automatic name.'
            in warnings_msgs)

    assert warnings[1].level == WARNING
    assert warnings[1].id.startswith(CHECK_NAME)
    assert ('Migration main_app.0005_auto_20200329_1118 has an automatic name.'
            in warnings_msgs)


@pytest.mark.django_db
def test_autonames_with_ignore(ignore_migration):
    """Here we check that some migrations can be ignored."""
    warnings = check_migration_names()

    assert not warnings


@pytest.mark.django_db
def test_autonames_with_ignore_all_app_migrations(
        ignore_migration_with_special_key):
    """Here we check that all migrations ignored inside app."""
    warnings = check_migration_names()

    assert not warnings
