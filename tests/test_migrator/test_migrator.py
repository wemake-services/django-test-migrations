import pytest
from django.db.migrations.state import ProjectState

from django_test_migrations.migrator import Migrator


@pytest.mark.django_db
def test_migrator(transactional_db):
    """We only need this test for coverage."""
    migrator = Migrator()
    old_state = migrator.before(('main_app', None))
    new_state = migrator.after(('main_app', '0001_initial'))

    assert isinstance(old_state, ProjectState)
    assert isinstance(new_state, ProjectState)
    assert migrator.reset() is None


@pytest.mark.django_db
def test_migrator_list(transactional_db):
    """We only need this test for coverage."""
    migrator = Migrator()
    old_state = migrator.before([('main_app', None)])
    new_state = migrator.after([('main_app', '0001_initial')])

    assert isinstance(old_state, ProjectState)
    assert isinstance(new_state, ProjectState)
    assert migrator.reset() is None
