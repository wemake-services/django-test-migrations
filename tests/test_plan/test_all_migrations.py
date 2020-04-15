import pytest

from django_test_migrations.plan import all_migrations, nodes_to_tuples


@pytest.mark.django_db
def test_all_migrations_main():
    """Testing migrations for a single app only."""
    main_migrations = all_migrations('default', ['main_app'])

    assert nodes_to_tuples(main_migrations) == [
        ('main_app', '0001_initial'),
        ('main_app', '0002_someitem_is_clean'),
        ('main_app', '0003_update_is_clean'),
        ('main_app', '0004_auto_20191119_2125'),
        ('main_app', '0005_auto_20200329_1118'),
    ]


@pytest.mark.django_db
def test_all_migrations_missing():
    """Testing migrations for a missing app."""
    with pytest.raises(LookupError):
        all_migrations('default', ['missing_app'])


@pytest.mark.django_db
def test_all_migrations_auth():
    """Testing migrations for a builtin app."""
    auth_migrations = all_migrations('default', ['auth'])
    assert len(auth_migrations) >= 10


@pytest.mark.django_db
def test_all_migrations_all():
    """Testing migrations for all apps."""
    assert len(all_migrations()) >= 17  # noqa: WPS432
