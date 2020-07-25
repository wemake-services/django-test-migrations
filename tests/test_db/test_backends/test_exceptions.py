from django_test_migrations.db.backends import exceptions


def test_database_configuration_not_found():
    """Ensure exception returns proper string representation."""
    vendor = 'ms_sql'
    exception = exceptions.DatabaseConfigurationNotFound(vendor)
    assert vendor in str(exception)


def test_database_configuration_setting_not_found():
    """Ensure exception returns proper string representation."""
    vendor = 'ms_sql'
    setting_name = 'fake_setting'
    exception = exceptions.DatabaseConfigurationSettingNotFound(
        vendor,
        setting_name,
    )
    assert vendor in str(exception)
    assert setting_name in str(exception)
