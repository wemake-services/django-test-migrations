from typing import Any

from django.core.management import call_command
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.migration import Migration
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


class SubstitutableMigrationLoader(MigrationLoader):
    """
    Class to allow for on-the-fly migration substitution
    """

    def __init__(self, *args, **kwargs):
        self.substituted_migrations = {}
        super().__init__(*args, **kwargs)
        # initializes as None, we need a dict to apply when load=False
        self.disk_migrations = {}

    def substitute_migration(
        self, target: MigrationTarget, migration: Migration
    ) -> None:
        """Substitute a target migration with a given migration"""
        self.substituted_migrations[target] = migration
        self._apply_substitutions()

    def _apply_substitutions(self):
        self.disk_migrations.update(self.substituted_migrations)

    def load_disk(self) -> None:
        """Override parent method to substitute patched migrations"""
        super().load_disk()
        self._apply_substitutions()


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
        # load=True to ensure loader.disk_migrations is populated before substitution
        self._executor.loader = SubstitutableMigrationLoader(
            connections[self._database], load=True
        )

    def _set_run_before(
        self, migrations: MigrationSpec, run_before: MigrationSpec
    ) -> None:
        """Adds migrations to the run_before attribute of target migrations"""
        migrations = normalize(migrations)
        run_before = normalize(run_before)
        for from_migration in migrations:
            migration = self._executor.loader.get_migration(*from_migration)
            for to_migration in run_before:
                if (
                    to_migration not in migration.dependencies
                    and to_migration not in migration.run_before
                ):
                    migration.run_before.append(to_migration)
            self._executor.loader.substitute_migration(
                from_migration, migration
            )

    def _get_roots(self, migration: MigrationTarget):
        all_roots = []
        roots = self._executor.loader.graph.root_nodes(app=migration[0])
        for root in roots:
            if (
                root[0] == migration[0] and root not in all_roots
            ):  # only add roots from this app
                all_roots.append(root)
        return all_roots

    def apply_initial_migration(
        self, targets: MigrationSpec, run_before: MigrationSpec = []
    ) -> ProjectState:
        """Reverse back to the original migration."""
        targets = normalize(targets)
        run_before = normalize(run_before)

        style = no_style()
        # start from clean database state
        sql.drop_models_tables(self._database, style)
        sql.flush_django_migrations_table(self._database, style)
        self._executor.loader.build_graph()  # reload

        # if specifying None as a target migration, add the initial migration(s)
        # for that app to run_before to ensure no migrations are applied
        for t in targets:
            if t[1] is None:
                roots = self._get_roots(t)
                for root in roots:
                    if root not in run_before:  # only add roots from this app
                        run_before.append(root)

        # ensure targets are migrated before the run_before
        target_plan = [
            (m.app_label, m.name)
            for m, _ in self._executor.migration_plan(targets, clean_start=True)
        ]
        not_none_targets = [t for t in targets if t[1] is not None]
        for b in run_before:  # check each individually to support mixing forward and reverse migrations in a plan
            if b[1] is not None and b not in target_plan:
                self._set_run_before(not_none_targets, b)

        # prepare as broad plan as possible based on full plan
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
        https://code.djangoproject.com/ticket/36061 where
        ``through_fields`` is lost when building ``ProjectState`` instance.
        Ticket #36061 was fixed in
        https://github.com/django/django/pull/19006

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
