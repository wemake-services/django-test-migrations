from typing import Optional

import pytest
from django.db import DEFAULT_DB_ALIAS

from django_test_migrations.constants import MIGRATION_TEST_MARKER


def pytest_load_initial_conftests(early_config):
    """Register pytest's markers."""
    early_config.addinivalue_line(
        'markers',
        "{0}: mark the test as a Django's migration test.".format(
            MIGRATION_TEST_MARKER,
        ),
    )


def pytest_collection_modifyitems(session, items):  # noqa: WPS110
    """Mark all tests using ``migrator_factory`` fixture with proper marks.

    Add ``MIGRATION_TEST_MARKER`` marker to all items using
    ``migrator_factory`` fixture.

    """
    for pytest_item in items:
        if 'migrator_factory' in getattr(pytest_item, 'fixturenames', []):
            pytest_item.add_marker(MIGRATION_TEST_MARKER)


@pytest.fixture()
def migrator_factory(request, transactional_db, django_db_use_migrations):
    """
    Pytest fixture to create migrators inside the pytest tests.

    How? Here's an example.

    .. code:: python

        @pytest.mark.django_db
        def test_migration(migrator_factory):
            migrator = migrator_factory('custom_db_alias')
            old_state = migrator.apply_initial_migration(('main_app', None))
            new_state = migrator.apply_tested_migration(
                ('main_app', '0001_initial'),
            )

            assert isinstance(old_state, ProjectState)
            assert isinstance(new_state, ProjectState)

    Why do we import :class:`Migrator` inside the fixture function?
    Otherwise, coverage won't work correctly during our internal tests.
    Why? Because modules in Python are singletons.
    Once imported, they will be stored in memory and reused.

    That's why we cannot import ``Migrator`` on a module level.
    Because it won't be caught be coverage later on.
    """
    from django_test_migrations.migrator import Migrator  # noqa: WPS433

    if not django_db_use_migrations:
        pytest.skip('--nomigrations was specified')

    def factory(database_name: Optional[str] = None) -> Migrator:
        migrator = Migrator(database_name)
        request.addfinalizer(migrator.reset)  # noqa: PT021
        return migrator
    return factory


@pytest.fixture()
def migrator(migrator_factory):  # noqa: WPS442
    """
    Useful alias for ``'default'`` database in ``django``.

    That's a predefined instance of a ``migrator_factory``.

    How to use it? Here's an example.

    .. code:: python

        @pytest.mark.django_db
        def test_migration(migrator):
            old_state = migrator.apply_initial_migration(('main_app', None))
            new_state = migrator.apply_tested_migration(
                ('main_app', '0001_initial'),
            )

            assert isinstance(old_state, ProjectState)
            assert isinstance(new_state, ProjectState)

    Just one step easier than ``migrator_factory`` fixture.
    """
    return migrator_factory(DEFAULT_DB_ALIAS)
