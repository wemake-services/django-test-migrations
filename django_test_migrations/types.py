from typing import List, Optional, Tuple, Union

from django.db import DefaultConnectionProxy
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.migrations import Migration

# Migration target: (app_name, migration_name)
# Regular or rollback migration: 0001 -> 0002, or 0002 -> 0001
# Rollback migration to initial state: 0001 -> None
MigrationTarget = Tuple[str, Optional[str]]
MigrationSpec = Union[MigrationTarget, List[MigrationTarget]]

MigrationPlan = List[Tuple[Migration, bool]]

AnyConnection = Union[DefaultConnectionProxy, BaseDatabaseWrapper]

DatabaseSettingValue = Union[str, int]
