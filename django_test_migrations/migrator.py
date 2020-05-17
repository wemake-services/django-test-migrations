from contextlib import contextmanager
from typing import Optional

from django.core.management import call_command
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState
from django.db.models.signals import post_migrate, pre_migrate

from django_test_migrations import sql
from django_test_migrations.logic.migrations import normalize
from django_test_migrations.plan import truncate_plan
from django_test_migrations.types import MigrationPlan, MigrationSpec


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

    def apply_initial_migration(self, targets: MigrationSpec) -> ProjectState:
        """Reverse back to the original migration."""
        targets = normalize(targets)

        style = no_style()
        # start from clean database state
        sql.drop_models_tables(self._database, style)
        sql.flush_django_migrations_table(self._database, style)

        # prepare as broad plan as possible based on full plan
        self._executor.loader.build_graph()  # reload
        full_plan = self._executor.migration_plan(
            self._executor.loader.graph.leaf_nodes(),
            clean_start=True,
        )
        plan = truncate_plan(targets, full_plan)

        # apply all migrations from generated plan on clean database
        # (only forward, so any unexpected migration won't be applied)
        # to restore database state before tested migration
        return self._migrate(targets, plan=plan)

    def apply_tested_migration(self, targets: MigrationSpec) -> ProjectState:
        """Apply the next migration."""
        self._executor.loader.build_graph()  # reload
        return self._migrate(normalize(targets))

    def reset(self) -> None:
        """Reset the state to the most recent one."""
        call_command('migrate', verbosity=0, database=self._database)

    def _migrate(
        self,
        migration_targets: MigrationSpec,
        plan: Optional[MigrationPlan] = None,
    ) -> ProjectState:
        with _mute_migrate_signals():
            return self._executor.migrate(migration_targets, plan=plan)
