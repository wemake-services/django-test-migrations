import pytest
from django.db.migrations.state import ProjectState
from django_test_migrations.migrator import Migrator


@pytest.mark.django_db
def test_migrator(transactional_db):
    """We only need this test for coverage."""
    migrator = Migrator()
    old_state = migrator.apply_initial_migration(('main_app', None))
    new_state = migrator.apply_tested_migration(('main_app', '0001_initial'))

    assert isinstance(old_state, ProjectState)
    assert isinstance(new_state, ProjectState)
    assert migrator.reset() is None


@pytest.mark.django_db
def test_migrator_list(transactional_db):
    """We only need this test for coverage."""
    migrator = Migrator()
    old_state = migrator.apply_initial_migration([('main_app', None)])
    new_state = migrator.apply_tested_migration([('main_app', '0001_initial')])

    assert isinstance(old_state, ProjectState)
    assert isinstance(new_state, ProjectState)
    assert migrator.reset() is None


@pytest.mark.django_db
def test_migrator_sets_run_before_if_forward_migration(transactional_db):
    migrator = Migrator()
    from_migration = ('main_app', '0001_initial')
    to_migration = ('main_app', '0002_someitem_is_clean')

    migrator._set_run_before(from_migration, to_migration)

    assert to_migration in migrator._executor.loader.disk_migrations[from_migration].run_before


@pytest.mark.django_db
def test_migrator_ignores_run_before_if_backwards_migration(transactional_db):
    migrator = Migrator()
    from_migration = ('main_app', '0002_someitem_is_clean')
    to_migration = ('main_app', '0001_initial')

    migrator._set_run_before(from_migration, to_migration)

    assert not to_migration in migrator._executor.loader.disk_migrations[from_migration].run_before


@pytest.mark.django_db
def test_migrator_ignores_run_before_if_backwards_to_None(transactional_db):
    migrator = Migrator()
    from_migration = ('main_app', '0001_initial')
    to_migration = ('main_app', None)

    migrator.apply_initial_migration(from_migration, run_before=to_migration)

    assert not to_migration in migrator._executor.loader.disk_migrations[from_migration].run_before


@pytest.mark.django_db
def test_migrator_ignores_run_before_if_target_None(transactional_db):
    migrator = Migrator()
    from_migration = ('main_app', None)
    to_migration = ('main_app', '0001_initial')

    # should run without error, no explicit assertion
    migrator.apply_initial_migration(from_migration, run_before=to_migration)


@pytest.mark.django_db
def test_migrator_gets_roots(transactional_db):
    migrator = Migrator()
    target = ('main_app', None)
    roots = [('main_app', '0001_initial')]

    assert migrator._get_roots(target) == roots


@pytest.mark.django_db
def test_migrator_gets_only_this_app_roots(transactional_db, mocker):
    migrator = Migrator()
    target = ('main_app', None)
    roots = [('main_app', '0001_initial')]

    migrator._executor.loader.graph.root_nodes=lambda *args, **kwargs: roots + [('another_app', '0001_initial')]

    # should exclude another_app root
    assert migrator._get_roots(target) == roots
