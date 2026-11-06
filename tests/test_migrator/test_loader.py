import pytest
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.migration import Migration

from django_test_migrations.migrator import SubstitutableMigrationLoader


@pytest.mark.django_db
def test_loader_records_substitution(transactional_db):
    loader = SubstitutableMigrationLoader(
        connections[DEFAULT_DB_ALIAS], load=False
    )
    migration = ('test', '0001_initial')
    loader.substitute_migration(migration, Migration(*migration))

    assert migration in loader.substituted_migrations


@pytest.mark.django_db
def test_loader_substitutes_on_load(transactional_db, mocker):
    loader = SubstitutableMigrationLoader(
        connections[DEFAULT_DB_ALIAS], load=False
    )
    migration = ('test', '0001_initial')
    loader.substitute_migration(migration, Migration(*migration))

    mocker.patch('django_test_migrations.migrator.MigrationLoader.load_disk')
    loader.disk_migrations = {}  # initializes as None

    loader.load_disk()
    assert migration in loader.disk_migrations
