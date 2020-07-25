import datetime

import pytest

from django_test_migrations.logic.datetime import timedelta_to_miliseconds


@pytest.mark.parametrize(('timedelta', 'expected_result'), [
    (datetime.timedelta(seconds=1), 1000),
    (datetime.timedelta(minutes=3), 3 * 60 * 1000),
    (datetime.timedelta(hours=2.6), 2.6 * 60 * 60 * 1000),
    (datetime.timedelta(days=4), 4 * 24 * 60 * 60 * 1000),
    (datetime.timedelta(minutes=7.4, seconds=47), 7.4 * 60 * 1000 + 47 * 1000),
])
def test_timedelta_to_miliseconds(timedelta, expected_result):
    """Ensure expected value is returned."""
    assert timedelta_to_miliseconds(timedelta) == expected_result
