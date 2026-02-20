from unittest.mock import MagicMock

import pytest
from django.db.migrations.state import ModelState, ProjectState
from django.db.models import ManyToManyField
from django.db.models.fields.reverse_related import ManyToManyRel

from django_test_migrations.migrator import Migrator


@pytest.mark.django_db(transaction=True)
def test_fix_through_fields_regression():
    """Ensure that through_fields are preserved in the project state.

    This is a regression test for https://github.com/wemake-services/django-test-migrations/issues/418
    (and the underlying Django issue).

    """
    migrator = Migrator()

    migrator.apply_initial_migration(('main_app', '0005_auto_20200329_1118'))
    new_state = migrator.apply_tested_migration(
        ('main_app', '0006_fix_through_fields'),
    )

    SomeGroup = new_state.apps.get_model('main_app', 'SomeGroup')
    members_field = SomeGroup._meta.get_field('members')  # noqa: SLF001
    assert members_field.remote_field.through_fields == ('group', 'member')


@pytest.mark.django_db
def test_fix_through_fields_logic():
    """Ensure that through_fields are preserved in the project state."""
    mock_remote_field = MagicMock(spec=ManyToManyRel, through_fields=None)
    mock_project_state = MagicMock(spec=ProjectState)
    mock_model = mock_project_state.apps.get_model.return_value
    mock_model._meta.get_field.return_value.remote_field = mock_remote_field
    mock_project_state.models = {
        ('my_app', 'my_model'): MagicMock(
            spec=ModelState,
            fields={
                'my_field': MagicMock(
                    spec=ManyToManyField,
                    many_to_many=True,
                    remote_field=MagicMock(
                        spec=ManyToManyRel,
                        through_fields=('foo', 'bar'),
                    ),
                ),
            },
        ),
    }

    Migrator()._fix_through_fields(mock_project_state)  # noqa: SLF001

    assert mock_remote_field.through_fields == ('foo', 'bar')
    mock_project_state.apps.get_model.assert_called_with('my_app', 'my_model')


@pytest.mark.django_db
def test_fix_through_fields_logic_no_update():
    """Ensure that ``through_fields`` are not updated when already present."""
    mock_remote_field = MagicMock(
        spec=ManyToManyRel,
        through_fields=('existing', 'value'),
    )
    mock_project_state = MagicMock(spec=ProjectState)
    mock_model = mock_project_state.apps.get_model.return_value
    mock_field = mock_model._meta.get_field.return_value  # noqa: SLF001
    mock_field.remote_field = mock_remote_field
    mock_project_state.models = {
        ('my_app', 'my_model'): MagicMock(
            spec=ModelState,
            fields={
                'my_field': MagicMock(
                    spec=ManyToManyField,
                    many_to_many=True,
                    remote_field=MagicMock(
                        spec=ManyToManyRel,
                        through_fields=('foo', 'bar'),
                    ),
                ),
            },
        ),
    }

    Migrator()._fix_through_fields(mock_project_state)  # noqa: SLF001

    assert mock_remote_field.through_fields == ('existing', 'value')


@pytest.mark.django_db
def test_fix_through_fields_logic_no_source_fields():
    """Ensure that nothing happens when source has no ``through_fields``."""
    mock_remote_field = MagicMock(spec=ManyToManyRel, through_fields=None)
    mock_project_state = MagicMock(spec=ProjectState)
    mock_project_state.models = {
        ('my_app', 'my_model'): MagicMock(
            spec=ModelState,
            fields={
                'my_field': MagicMock(
                    spec=ManyToManyField,
                    many_to_many=True,
                    remote_field=MagicMock(
                        spec=ManyToManyRel,
                        through_fields=None,
                    ),
                ),
            },
        ),
    }

    Migrator()._fix_through_fields(mock_project_state)  # noqa: SLF001

    assert not mock_remote_field.through_fields
    mock_project_state.apps.get_model.assert_not_called()


@pytest.mark.django_db
def test_fix_through_fields_logic_not_m2m():
    """Ensure that non-many-to-many fields are ignored."""
    mock_remote_field = MagicMock(spec=ManyToManyRel, through_fields=None)
    mock_project_state = MagicMock(spec=ProjectState)
    mock_project_state.models = {
        ('my_app', 'my_model'): MagicMock(
            spec=ModelState,
            fields={
                'my_field': MagicMock(
                    spec=ManyToManyField,
                    many_to_many=False,
                    remote_field=MagicMock(
                        spec=ManyToManyRel,
                        through_fields=('foo', 'bar'),
                    ),
                ),
            },
        ),
    }

    Migrator()._fix_through_fields(mock_project_state)  # noqa: SLF001

    assert not mock_remote_field.through_fields
    mock_project_state.apps.get_model.assert_not_called()
