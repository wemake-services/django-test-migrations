import pytest


@pytest.fixture()
def ignore_migration(settings):
    """We patch settings to ignore this one bad migration."""
    settings.DTM_IGNORED_MIGRATIONS = {
        ('main_app', '0004_auto_20191119_2125'),
        ('main_app', '0005_auto_20200329_1118'),
    }
    return settings


@pytest.fixture()
def ignore_migration_with_special_key(settings):
    """We patch settings to ignore all migrations in the app."""
    settings.DTM_IGNORED_MIGRATIONS = {
        ('main_app', '*'),
    }
    return settings
