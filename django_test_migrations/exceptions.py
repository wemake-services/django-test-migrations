from django_test_migrations.types import MigrationTarget


class MigrationNotInPlan(Exception):
    """``MigrationTarget`` not found in migrations plan."""

    def __init__(self, migration_target: MigrationTarget) -> None:  # noqa: D107
        self.migration_target = migration_target

    def __str__(self) -> str:
        """String representation of exception's instance."""
        return 'Migration {0} not found in migrations plan'.format(
            self.migration_target,
        )
