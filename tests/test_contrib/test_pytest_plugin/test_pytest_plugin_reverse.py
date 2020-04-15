"""
This module covers tests for migration rollbacks.

It might be useful when something goes wrong
and you need to switch back to the previous state.
"""

import pytest
from django.core.exceptions import FieldError


@pytest.mark.django_db
def test_pytest_plugin0001(migrator):
    """Ensures that the first migration works."""
    old_state = migrator.before(('main_app', '0002_someitem_is_clean'))
    SomeItem = old_state.apps.get_model('main_app', 'SomeItem')

    assert SomeItem.objects.filter(is_clean=True).count() == 0

    new_state = migrator.after(('main_app', '0001_initial'))
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')

    with pytest.raises(FieldError):
        SomeItem.objects.filter(is_clean=True)


@pytest.mark.django_db
def test_pytest_plugin0002(migrator):
    """Ensures that the second migration works."""
    old_state = migrator.before(('main_app', '0003_update_is_clean'))
    SomeItem = old_state.apps.get_model('main_app', 'SomeItem')
    SomeItem.objects.create(string_field='a', is_clean=True)
    SomeItem.objects.create(string_field='a b', is_clean=False)

    assert SomeItem.objects.count() == 2
    assert SomeItem.objects.filter(is_clean=True).count() == 1

    new_state = migrator.after(('main_app', '0002_someitem_is_clean'))
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')

    assert SomeItem.objects.count() == 2
    assert SomeItem.objects.filter(is_clean=True).count() == 1
