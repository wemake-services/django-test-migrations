import pytest

from django_test_migrations.exceptions import MigrationNotInPlan
from django_test_migrations.plan import truncate_plan


@pytest.mark.parametrize(
    ('targets', 'index'),
    [
        ([], 9),  # full plan for empty targets
        ([('app1', None)], 0),
        ([('app1', None), ('app3', None)], 7),
        ([('app2', '0002_second')], 6),
        ([('app1', '0002_second'), ('app2', None)], 2),
        ([('app1', '0003_third'), ('app2', None)], 4),
        ([('app1', '0003_third'), ('app1', '0005_fifth')], 7),
        ([('app1', '0003_third'), ('app2', None), ('app3', '0001_initial')], 8),
    ],
)
def test_truncate_plan(plan, targets, index):
    """Ensure plan is properly truncated for both types migrations names."""
    assert truncate_plan(targets, plan) == plan[:index]


def test_empty_plan():
    """Ensure function work when plan is empty."""
    assert not truncate_plan([('app1', '0001_initial')], [])


@pytest.mark.parametrize(
    'targets',
    [
        [('app4', None)],
        [('app1', '0047_magic')],
        [('app1', '0005_fifth'), ('app4', None)],
        [('app1', '0005_fifth'), ('app4', '0047_magic'), ('app3', None)],
    ],
)
def test_migration_target_does_not_exist(plan, targets):
    """Ensure ``MigrationNotInPlan`` is raised when target not in plan."""
    with pytest.raises(MigrationNotInPlan):
        truncate_plan(targets, plan)
