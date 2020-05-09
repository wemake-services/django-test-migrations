from typing import List

from django_test_migrations.types import MigrationSpec, MigrationTarget


def normalize(migration_target: MigrationSpec) -> List[MigrationTarget]:
    """Normalize ``migration_target`` to expected format."""
    if not isinstance(migration_target, list):
        migration_target = [migration_target]
    return migration_target
