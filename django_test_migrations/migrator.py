from contextlib import contextmanager
from typing import List, Optional, Tuple, Union

from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState
from django.db.models.signals import post_migrate, pre_migrate

# Regular or rollback migration: 0001 -> 0002, or 0002 -> 0001
# Rollback migration to initial state: 0001 -> None
_Migration = Tuple[str, Optional[str]]
_MigrationSpec = Union[_Migration, List[_Migration]]


@contextmanager
def _mute_migrate_signals():
    """
    Mutes post_migrate and pre_migrate signals that breaks during testing.

    This context manager just turns them off temporarly.

    Related:
    https://github.com/wemake-services/django-test-migrations/issues/11
    """
    restore_post, post_migrate.receivers = (  # noqa: WPS414
        post_migrate.receivers, [],
    )
    restore_pre, pre_migrate.receivers = (  # noqa: WPS414
        pre_migrate.receivers, [],
    )

    yield

    post_migrate.receivers = restore_post
    pre_migrate.receivers = restore_pre


class Migrator(object):
    """
    Class to manage your migrations and app state.

    It is designed to be used inside the tests to ensure that migrations
    are working as intended: both data and schema migrations.

    This class can be but probably should not be used directly.
    Because we have utility test framework
    integrations for ``unitest`` and ``pytest``.

    Use them for better experience.
    """

    def __init__(
        self,
        database: Optional[str] = None,
    ) -> None:
        """That's where we initialize all required internals."""
        if database is None:
            database = DEFAULT_DB_ALIAS

        self._database: str = database
        self._executor = MigrationExecutor(connections[self._database])

    def before(self, migrate_from: _MigrationSpec) -> ProjectState:
        """Reverse back to the original migration."""
        if not isinstance(migrate_from, list):
            migrate_from = [migrate_from]
        with _mute_migrate_signals():
            return self._executor.migrate(migrate_from)

    def after(self, migrate_to: _MigrationSpec) -> ProjectState:
        """Apply the next migration."""
        self._executor.loader.build_graph()  # reload.
        return self.before(migrate_to)

    def reset(self) -> None:
        """Reset the state to the most recent one."""
        call_command(
            'flush',
            database=self._database,
            interactive=False,
            verbosity=0,
        )
