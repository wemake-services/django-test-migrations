from typing import List, Optional, Tuple, Union

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.migrations import Migration
from django.utils.connection import ConnectionProxy
from typing_extensions import TypeAlias

# Migration target: (app_name, migration_name)
# Regular or rollback migration: 0001 -> 0002, or 0002 -> 0001
# Rollback migration to initial state: 0001 -> None
MigrationTarget: TypeAlias = Tuple[str, Optional[str]]
MigrationSpec: TypeAlias = Union[MigrationTarget, List[MigrationTarget]]

MigrationPlan: TypeAlias = List[Tuple[Migration, bool]]

AnyConnection: TypeAlias = Union[ConnectionProxy, BaseDatabaseWrapper]

DatabaseSettingValue: TypeAlias = Union[str, int]
