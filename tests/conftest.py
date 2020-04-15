import pytest


@pytest.fixture(scope='session')
def django_db_use_migrations(
    request,
    django_db_use_migrations,  # noqa: WPS442
):
    """
    Helper fixture to skip tests when ``--nomigrations`` were specified.

    Copied from https://github.com/pytest-dev/pytest-django
    """
    if not django_db_use_migrations:
        pytest.skip('--nomigrations was specified')
    return django_db_use_migrations
