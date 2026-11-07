import pytest

from django_test_migrations.plan import find_maximum_plan_depth


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
