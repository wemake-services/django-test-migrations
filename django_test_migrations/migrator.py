from typing import Any

from django.core.management import call_command
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState
from django.db.models import ManyToManyField

from django_test_migrations import sql
from django_test_migrations.logic.migrations import normalize
from django_test_migrations.plan import truncate_plan
from django_test_migrations.signals import mute_migrate_signals
from django_test_migrations.types import (
    MigrationPlan,
    MigrationSpec,
    MigrationTarget,
)


class Migrator:
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
        database: str | None = None,
    ) -> None:
        """That's where we initialize all required internals."""
        if database is None:
            database = DEFAULT_DB_ALIAS

        self._database: str = database
        self._executor = MigrationExecutor(connections[self._database])

    def apply_initial_migration(self, targets: MigrationSpec) -> ProjectState:
        """Reverse back to the original migration."""
        migration_targets = normalize(targets)

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
        plan = truncate_plan(migration_targets, full_plan)

        # apply all migrations from generated plan on clean database
        # (only forward, so any unexpected migration won't be applied)
        # to restore database state before tested migration
        return self._migrate(migration_targets, plan=plan)

    def apply_tested_migration(self, targets: MigrationSpec) -> ProjectState:
        """Apply the next migration."""
        self._executor.loader.build_graph()  # reload
        return self._migrate(normalize(targets))

    def reset(self) -> None:
        """
        Reset the state to the most recent one.

        Notably, signals are not muted here to avoid
        https://github.com/wemake-services/django-test-migrations/issues/128

        """
        call_command('migrate', verbosity=0, database=self._database)

    def _migrate(
        self,
        migration_targets: list[MigrationTarget],
        plan: MigrationPlan | None = None,
    ) -> ProjectState:
        with mute_migrate_signals():
            project_state = self._executor.migrate(migration_targets, plan=plan)
            project_state.clear_delayed_apps_cache()
            self._fix_through_fields(project_state)
            return project_state

    def _fix_through_fields(self, project_state: ProjectState) -> None:
        """Fix ``through_fields`` in many-to-many fields for ``project_state``.

        This is a workaround for Django issue
        ([Ticket #36061](https://code.djangoproject.com/ticket/36061)) where
        ``through_fields`` is lost when building ``ProjectState`` instance.
        Ticket #36061 was fixed in
        [PR #19006](https://github.com/django/django/pull/19006).

        """
        for (
            app_label,
            model_name,
        ), model_state in project_state.models.items():  # pragma: no cover
            for field_name, field in model_state.fields.items():
                if field.many_to_many:
                    self._restore_through_fields(
                        project_state,
                        app_label,
                        model_name,
                        field_name,
                        field,
                    )

    def _restore_through_fields(
        self,
        project_state: ProjectState,
        app_label: str,
        model_name: str,
        field_name: str,
        field: 'ManyToManyField[Any, Any]',
    ) -> None:
        """Restores ``through_fields`` from ``field`` to ``project_state``."""
        through_fields = getattr(
            field.remote_field,
            'through_fields',
            None,
        )
        if not through_fields:
            return
        model = project_state.apps.get_model(app_label, model_name)
        model_field = model._meta.get_field(field_name)  # noqa: SLF001
        model_remote = getattr(model_field, 'remote_field', None)
        if model_remote and not getattr(model_remote, 'through_fields', None):
            model_remote.through_fields = through_fields
