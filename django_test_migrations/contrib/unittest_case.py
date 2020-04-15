from typing import ClassVar, Optional

from django.db.migrations.state import ProjectState
from django.test import TransactionTestCase

from django_test_migrations.migrator import Migrator, _Migration  # noqa: WPS450


class MigratorTestCase(TransactionTestCase):
    """Used when using raw ``unitest`` library for test."""

    database_name: ClassVar[Optional[str]] = None
    old_state: ProjectState
    new_state: ProjectState

    #: Part of the end-user API. Used to tell what migrations we are using.
    migrate_from: ClassVar[_Migration]
    migrate_to: ClassVar[_Migration]

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
        self.old_state = self._migrator.before(self.migrate_from)
        self.prepare()
        self.new_state = self._migrator.after(self.migrate_to)

    def prepare(self) -> None:
        """
        Part of the end-user API.

        Used to prepare some data before the migration process.
        """
