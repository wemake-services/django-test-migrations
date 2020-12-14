from typing import List, Optional, Tuple, Union

import django
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.migrations import Migration

if django.VERSION < (3, 2):
    from django.db import (  # noqa: WPS433
        DefaultConnectionProxy as ConnectionProxy,
    )
else:
    from django.utils.connection import ConnectionProxy  # noqa: WPS440, WPS433

# Migration target: (app_name, migration_name)
# Regular or rollback migration: 0001 -> 0002, or 0002 -> 0001
# Rollback migration to initial state: 0001 -> None
MigrationTarget = Tuple[str, Optional[str]]
MigrationSpec = Union[MigrationTarget, List[MigrationTarget]]

MigrationPlan = List[Tuple[Migration, bool]]

AnyConnection = Union[ConnectionProxy, BaseDatabaseWrapper]

DatabaseSettingValue = Union[str, int]
