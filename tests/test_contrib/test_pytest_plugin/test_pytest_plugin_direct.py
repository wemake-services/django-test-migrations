"""
This module covers simple direct migrations.

We test both schema and data-migrations here.
"""

import pytest
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_pytest_plugin_initial(migrator):
    """Ensures that the initial migration works."""
    old_state = migrator.before(('main_app', None))

    with pytest.raises(LookupError):
        # Models does not yet exist:
        old_state.apps.get_model('main_app', 'SomeItem')

    new_state = migrator.after(('main_app', '0001_initial'))
    # After the initial migration is done, we can use the model state:
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')
    assert SomeItem.objects.filter(string_field='').count() == 0


@pytest.mark.django_db
def test_pytest_plugin0001(migrator):
    """Ensures that the first migration works."""
    old_state = migrator.before(('main_app', '0001_initial'))
    SomeItem = old_state.apps.get_model('main_app', 'SomeItem')

    with pytest.raises(FieldError):
        SomeItem.objects.filter(is_clean=True)

    new_state = migrator.after(('main_app', '0002_someitem_is_clean'))
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')

    assert SomeItem.objects.filter(is_clean=True).count() == 0


@pytest.mark.django_db
def test_pytest_plugin0002(migrator):
    """Ensures that the second migration works."""
    old_state = migrator.before(('main_app', '0002_someitem_is_clean'))
    SomeItem = old_state.apps.get_model('main_app', 'SomeItem')
    SomeItem.objects.create(string_field='a')
    SomeItem.objects.create(string_field='a b')

    assert SomeItem.objects.count() == 2
    assert SomeItem.objects.filter(is_clean=True).count() == 2

    new_state = migrator.after(('main_app', '0003_update_is_clean'))
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')

    assert SomeItem.objects.count() == 2
    assert SomeItem.objects.filter(is_clean=True).count() == 1


@pytest.mark.django_db
def test_pytest_plugin0003(migrator):
    """Ensures that the third migration works."""
    old_state = migrator.before(('main_app', '0003_update_is_clean'))
    SomeItem = old_state.apps.get_model('main_app', 'SomeItem')
    SomeItem.objects.create(string_field='a')  # default is still there

    assert SomeItem.objects.count() == 1
    assert SomeItem.objects.filter(is_clean=True).count() == 1

    new_state = migrator.after(('main_app', '0004_auto_20191119_2125'))
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')

    with pytest.raises(IntegrityError):
        SomeItem.objects.create(string_field='b')  # no default anymore
