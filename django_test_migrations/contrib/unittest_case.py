from typing import ClassVar, Optional

from django.db.migrations.state import ProjectState
from django.db.models.signals import post_migrate, pre_migrate
from django.test import TransactionTestCase, tag

from django_test_migrations.constants import MIGRATION_TEST_MARKER
from django_test_migrations.migrator import Migrator
from django_test_migrations.types import MigrationSpec


@tag(MIGRATION_TEST_MARKER)
class MigratorTestCase(TransactionTestCase):
    """Used when using raw ``unitest`` library for test."""

    database_name: ClassVar[Optional[str]] = None
    old_state: ProjectState
    new_state: ProjectState

    #: Part of the end-user API. Used to tell what migrations we are using.
    migrate_from: ClassVar[MigrationSpec]
    migrate_to: ClassVar[MigrationSpec]

    def setUp(self) -> None:
        """
        Regular ``unittest`` styled setup case.

        What it does?
          - It starts with defining the initial migration state
          - Then it allows to run custom method
            to prepare some data before the migration will happen
          - Then it applies the migration and saves all states

        """
        super().setUp()
        self._migrator = Migrator(self.database_name)
        self.old_state = self._migrator.apply_initial_migration(
            self.migrate_from,
        )
        self.prepare()
        self.new_state = self._migrator.apply_tested_migration(self.migrate_to)

    def prepare(self) -> None:
        """
        Part of the end-user API.

        Used to prepare some data before the migration process.
        """

    def tearDown(self) -> None:
        """Used to clean mess up after each test."""
        pre_migrate.receivers = self._pre_migrate_receivers
        post_migrate.receivers = self._post_migrate_receivers
        self._migrator.reset()
        super().tearDown()

    def _pre_setup(self) -> None:
        self._pre_migrate_receivers, pre_migrate.receivers = (  # noqa: WPS414
            pre_migrate.receivers, [],
        )
        self._post_migrate_receivers, post_migrate.receivers = (  # noqa: WPS414
            post_migrate.receivers, [],
        )
        super()._pre_setup()  # type: ignore[misc]
