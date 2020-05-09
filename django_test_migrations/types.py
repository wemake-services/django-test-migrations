from typing import List, Optional, Tuple, Union

# Migration target: (app_name, migration_name)
# Regular or rollback migration: 0001 -> 0002, or 0002 -> 0001
# Rollback migration to initial state: 0001 -> None
MigrationTarget = Tuple[str, Optional[str]]
MigrationSpec = Union[MigrationTarget, List[MigrationTarget]]
