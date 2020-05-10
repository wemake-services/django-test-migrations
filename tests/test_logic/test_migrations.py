from django_test_migrations.logic.migrations import normalize


def test_normalize_raw_target():
    """Ensure normalize works for ``MigrationTarget``."""
    assert normalize(('app', '0074_magic')) == [('app', '0074_magic')]


def test_normalize_list_of_targets():
    """Ensure normalize works for list of ``MigrationTarget``."""
    migration_targets = [('app1', None), ('app2', '0001_initial')]
    assert normalize(migration_targets) == migration_targets
