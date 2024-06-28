import django
import pytest
from django.apps import apps
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS
from django.db.models.signals import post_migrate, pre_migrate
from typing_extensions import Final

from django_test_migrations.signals import mute_migrate_signals

# value for ``dispatch_uid`` is needed to disconnect signal receiver
# registered for testing purposes to which we do not have any reference
# outside of test function
DISPATCH_UID: Final = 'test_migrate_signals'


# Dummy signal receiver function
def _my_callback(sender, **kwargs):
    """Mock that does nothing."""


@pytest.fixture
def _disconnect_receivers():
    """Disconnect testing receiver of ``pre_migrate`` or ``post_migrate``."""
    yield
    main_app_config = apps.get_app_config('main_app')
    pre_migrate.disconnect(sender=main_app_config, dispatch_uid=DISPATCH_UID)
    post_migrate.disconnect(sender=main_app_config, dispatch_uid=DISPATCH_UID)


@pytest.mark.parametrize('signal', [pre_migrate, post_migrate])
def test_migrate_signal_muted(signal):
    """Ensure the context manager does indeed silences the signals."""
    signal.connect(_my_callback)
    assert signal.receivers
    with mute_migrate_signals():
        assert not signal.receivers
    assert signal.receivers
    signal.disconnect(_my_callback)


@pytest.mark.skipif(
    django.VERSION >= (4, 0),
    reason='requires `Django<4.0`',
)
@pytest.mark.parametrize('signal', [pre_migrate, post_migrate])
@pytest.mark.usefixtures('migrator', '_disconnect_receivers')
def test_signal_receiver_registered_in_test(mocker, signal):
    """Ensure migration signal receivers registered in tests are called."""
    signal_receiver_mock = mocker.MagicMock()
    main_app_config = apps.get_app_config('main_app')
    signal.connect(
        signal_receiver_mock,
        sender=main_app_config,
        dispatch_uid=DISPATCH_UID,
    )
    verbosity = 0
    interactive = False
    # call `migrate` management command to trigger ``pre_migrate`` and
    # ``post_migrate`` signals
    call_command('migrate', verbosity=verbosity, interactive=interactive)

    signal_receiver_mock.assert_called_once_with(
        sender=main_app_config,
        app_config=main_app_config,
        apps=mocker.ANY,  # we don't have any reference to this object
        using=DEFAULT_DB_ALIAS,
        verbosity=verbosity,
        interactive=interactive,
        plan=mocker.ANY,  # not important for this test
        signal=signal,
    )


@pytest.mark.skipif(
    django.VERSION < (4, 0),
    reason='requires `Django>=4.0`',
)
@pytest.mark.parametrize('signal', [pre_migrate, post_migrate])
@pytest.mark.usefixtures('migrator', '_disconnect_receivers')
def test_signal_receiver_registered_in_test_django40(mocker, signal):
    """Ensure migration signal receivers registered in tests are called."""
    signal_receiver_mock = mocker.MagicMock()
    main_app_config = apps.get_app_config('main_app')
    signal.connect(
        signal_receiver_mock,
        sender=main_app_config,
        dispatch_uid=DISPATCH_UID,
    )
    verbosity = 0
    interactive = False
    # call `migrate` management command to trigger ``pre_migrate`` and
    # ``post_migrate`` signals
    call_command('migrate', verbosity=verbosity, interactive=interactive)

    signal_receiver_mock.assert_called_once_with(
        sender=main_app_config,
        app_config=main_app_config,
        apps=mocker.ANY,  # we don't have any reference to this object
        using=DEFAULT_DB_ALIAS,
        verbosity=verbosity,
        interactive=interactive,
        signal=signal,
        # following kwargs are not important for this test
        stdout=mocker.ANY,
        plan=mocker.ANY,
    )
