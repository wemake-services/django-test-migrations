from django_test_migrations.constants import MIGRATION_TEST_MARKER
from django_test_migrations.contrib.unittest_case import MigratorTestCase


class TestDirectMigration(MigratorTestCase):
    """This class is used to test direct migrations."""

    migrate_from = ('main_app', '0002_someitem_is_clean')
    migrate_to = ('main_app', '0003_update_is_clean')

    @classmethod
    def setUpClass(cls):
        """Override parent's setUpClass to trigger #503."""
        super().setUpClass()

    def prepare(self):
        """Prepare some data before the migration."""
        SomeItem = self.old_state.apps.get_model('main_app', 'SomeItem')
        SomeItem.objects.create(string_field='a')
        SomeItem.objects.create(string_field='a b')

    def test_migration_main0003(self):
        """Run the test itself."""
        SomeItem = self.new_state.apps.get_model('main_app', 'SomeItem')

        assert SomeItem.objects.count() == 2
        assert SomeItem.objects.filter(is_clean=True).count() == 1


class TestBackwardMigration(MigratorTestCase):
    """This class is used to test backward migrations."""

    migrate_from = ('main_app', '0002_someitem_is_clean')
    migrate_to = ('main_app', '0001_initial')

    def prepare(self):
        """Prepare some data before the migration."""
        SomeItem = self.old_state.apps.get_model('main_app', 'SomeItem')
        SomeItem.objects.create(string_field='a')
        SomeItem.objects.create(string_field='a b')

    def test_migration_main0001(self):
        """Run the test itself."""
        SomeItem = self.new_state.apps.get_model('main_app', 'SomeItem')

        assert SomeItem.objects.count() == 2


def test_migration_test_marker_tag():
    """Ensure ``MigratorTestCase`` subclasses are properly tagged."""
    assert MIGRATION_TEST_MARKER in TestDirectMigration.tags
    assert MIGRATION_TEST_MARKER in TestBackwardMigration.tags


class TestMigrationOrdering(MigratorTestCase):
    """Ensure we don't select migrations we intend to test as part of the initial migration"""

    migrate_from = [('main_app', None), ('another_app', '0001_initial')]
    migrate_to = [
        ('main_app', '0001_initial'),
        ('another_app', '0002_add_field'),
    ]

    def test_ensure_test_field_not_added_before(self):
        model = self.old_state.apps.get_model('another_app', 'DummyModel')
        assert 'test_field' not in [f.name for f in model._meta.fields]

    def test_ensure_test_field_added_after(self):
        model = self.new_state.apps.get_model('another_app', 'DummyModel')
        assert 'test_field' in [f.name for f in model._meta.fields]
