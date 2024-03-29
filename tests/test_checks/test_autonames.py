import pytest
from django.core.checks import WARNING

from django_test_migrations.checks.autonames import (
    CHECK_NAME,
    check_migration_names,
)


@pytest.mark.django_db()
def test_autonames():
    """Here we check that bad migrations do produce warnings."""
    warnings = check_migration_names()
    warnings_msgs = {warning.msg for warning in warnings}

    assert len(warnings) == 2

    assert [warnings[0].level, warnings[1].level] == [WARNING, WARNING]
    assert all(
        [
            warnings[0].id.startswith(CHECK_NAME),
            warnings[1].id.startswith(CHECK_NAME),
        ],
    )
    assert warnings_msgs == {
        'Migration main_app.0004_auto_20191119_2125 has an automatic name.',
        'Migration main_app.0005_auto_20200329_1118 has an automatic name.',
    }


@pytest.mark.django_db()
def test_autonames_with_ignore(settings):
    """Here we check that some migrations can be ignored."""
    # patch settings to ignore two bad migrations
    settings.DTM_IGNORED_MIGRATIONS = {
        ('main_app', '0004_auto_20191119_2125'),
        ('main_app', '0005_auto_20200329_1118'),
    }
    warnings = check_migration_names()

    assert not warnings


@pytest.mark.django_db()
def test_autonames_with_ignore_all_app_migrations(settings):
    """Here we check that all migrations ignored inside app."""
    # patch settings to ignore all migrations in the app
    settings.DTM_IGNORED_MIGRATIONS = {('main_app', '*')}
    warnings = check_migration_names()

    assert not warnings
