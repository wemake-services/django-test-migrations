from django_test_migrations.contrib.unittest_case import MigratorTestCase


class TestDirectMigration(MigratorTestCase):
    """This class is used to test direct migrations."""

    migrate_from = ('main_app', '0002_someitem_is_clean')
    migrate_to = ('main_app', '0003_update_is_clean')

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
