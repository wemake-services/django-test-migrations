from django_test_migrations.types import MigrationTarget


class MigrationNotInPlan(Exception):  # ruff: ignore[error-suffix-on-exception-name]
    """``MigrationTarget`` not found in migrations plan."""

    def __init__(self, migration_target: MigrationTarget) -> None:  # ruff: ignore[undocumented-public-init]
        self.migration_target = migration_target

    def __str__(self) -> str:
        """String representation of exception's instance."""
        return f'Migration {self.migration_target} not found in migrations plan'
