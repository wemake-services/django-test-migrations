import pytest

from django_test_migrations import exceptions


@pytest.mark.parametrize(
    ('target', 'expected_str'),
    [
        (('app', None), "Migration ('app', None) not found in migrations plan"),
        (
            ('app', '0047_magic'),
            "Migration ('app', '0047_magic') not found in migrations plan",
        ),
    ],
)
def test_representation(target, expected_str):
    """Ensure ``MigrationNotInPlan`` has expected string representation."""
    assert str(exceptions.MigrationNotInPlan(target)) == expected_str
