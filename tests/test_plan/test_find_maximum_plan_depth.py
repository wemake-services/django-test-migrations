import pytest
from django.db.migrations import Migration

from django_test_migrations.plan import (
    _has_exceeded_target,
    find_maximum_plan_depth,
)


def test_has_exceeded_target():
    """Encounter migration in app past target."""
    target = ('app1', '0001')
    seen = {target: True}
    migration = Migration('0002', 'app1')

    assert _has_exceeded_target([target], seen, migration)


def test_has_not_exceeded_target_reached_target():
    """Encounter target migration in app."""
    target = ('app1', '0001')
    seen = {target: False}
    migration = Migration('0001', 'app1')

    assert not _has_exceeded_target([target], seen, migration)
    assert seen[target]


def test_has_not_exceeded_target():
    """Encounter migration before target in app."""
    target = ('app1', '0002')
    seen = {target: False}
    migration = Migration('0001', 'app1')

    assert not _has_exceeded_target([target], seen, migration)


def test_has_exceeded_target_none():
    """Encounter migration from app when target None."""
    target = ('app1', None)
    seen = {target: True}
    migration = Migration('0001', 'app1')

    assert _has_exceeded_target([target], seen, migration)


def test_has_not_exceeded_target_other_app():
    """Encounter migration from other app."""
    target = ('app1', None)
    seen = {target: True}
    migration = Migration('0001', 'app2')

    assert not _has_exceeded_target([target], seen, migration)


@pytest.mark.parametrize(
    ('targets', 'index'),
    [
        ([], 8),  # full plan for empty targets
        ([('app1', None)], None),
        ([('app1', None), ('app3', None)], None),
        ([('app2', '0002_second')], 8),
        ([('app1', '0002_second'), ('app2', None)], 1),
        ([('app1', '0003_third'), ('app2', None)], 1),
        ([('app1', '0003_third'), ('app1', '0005_fifth')], 3),
        ([('app1', '0003_third'), ('app2', None), ('app3', '0001_initial')], 1),
        ([('app1', '0004_fourth')], 5)
    ],
)
def test_find_maximum_plan_depth(plan, targets, index):
    """Ensure plan is properly truncated for both types migrations names."""
    migration = (plan[index][0].app_label, plan[index][0].name) if index is not None else None
    assert find_maximum_plan_depth(targets, plan) == migration


def test_empty_plan():
    """Ensure function work when plan is empty."""
    assert not find_maximum_plan_depth([('app1', '0001_initial')], [])
