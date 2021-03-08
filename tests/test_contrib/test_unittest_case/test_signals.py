from unittest import mock

import django
import pytest
from django.apps import apps
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS
from django.db.models.signals import post_migrate, pre_migrate

from django_test_migrations.contrib.unittest_case import MigratorTestCase


class TestSignalMuting(MigratorTestCase):
    """Test that the `post_migrate` signal has been muted."""

    migrate_from = ('main_app', '0002_someitem_is_clean')
    migrate_to = ('main_app', '0001_initial')

    def test_pre_migrate_muted(self):
        """Ensure ``pre_migrate`` signal has been muted."""
        assert not pre_migrate.receivers

    def test_post_migrate_muted(self):
        """Ensure ``post_migrate`` signal has been muted."""
        assert not post_migrate.receivers


class TestSignalConnectInTest(MigratorTestCase):
    """Ensure test ``pre_migrate`` or ``post_migrate`` receiver are called.

    Ensure that ``pre_migrate`` or ``post_migrate`` signals receivers
    connected directly in tests are called.

    """

    migrate_from = ('main_app', '0001_initial')
    migrate_to = ('main_app', '0002_someitem_is_clean')

    def tearDown(self):
        """Disconnect ``pre_migrate`` and ``post_migrate`` testing receivers."""
        pre_migrate.disconnect(
            self.pre_migrate_receiver_mock,
            sender=self.main_app_config,
        )
        post_migrate.disconnect(
            self.post_migrate_receiver_mock,
            sender=self.main_app_config,
        )

    def prepare(self):
        """Connect testing ``pre_migrate`` and ``post_migrate`` receivers."""
        self.pre_migrate_receiver_mock = mock.MagicMock()
        self.post_migrate_receiver_mock = mock.MagicMock()
        # ``old_apps`` is not real ``ProjectState`` instance, so we cannot use
        # it to get "original" main_app ``AppConfig`` instance needed to
        # connect signal receiver, that's the reason we are using
        # ``apps`` imported directly from ``django.apps``
        self.main_app_config = apps.get_app_config('main_app')
        pre_migrate.connect(
            self.pre_migrate_receiver_mock,
            sender=self.main_app_config,
        )
        post_migrate.connect(
            self.post_migrate_receiver_mock,
            sender=self.main_app_config,
        )

    @pytest.mark.skipif(
        django.VERSION >= (4, 0),
        reason='requires `Django<4.0`',
    )
    def test_signal_receivers_added_in_tests(self):
        """Ensure migration signals receivers connected in tests are called."""
        verbosity = 0
        interactive = False
        # call `migrate` management command to trigger ``pre_migrate`` and
        # ``post_migrate`` signals
        call_command('migrate', verbosity=verbosity, interactive=interactive)

        common_kwargs = {
            'sender': self.main_app_config,
            'app_config': self.main_app_config,
            'apps': mock.ANY,  # we don't have any reference to this object
            'using': DEFAULT_DB_ALIAS,
            'verbosity': verbosity,
            'interactive': interactive,
            'plan': mock.ANY,  # not important for this test
        }
        self.pre_migrate_receiver_mock.assert_called_once_with(
            **common_kwargs,
            signal=pre_migrate,
        )
        self.post_migrate_receiver_mock.assert_called_once_with(
            **common_kwargs,
            signal=post_migrate,
        )

    @pytest.mark.skipif(
        django.VERSION < (4, 0),
        reason='requires `Django>=4.0`',
    )
    def test_signal_receivers_added_in_tests_django40(self):
        """Ensure migration signals receivers connected in tests are called."""
        verbosity = 0
        interactive = False
        # call `migrate` management command to trigger ``pre_migrate`` and
        # ``post_migrate`` signals
        call_command('migrate', verbosity=verbosity, interactive=interactive)

        common_kwargs = {
            'sender': self.main_app_config,
            'app_config': self.main_app_config,
            'apps': mock.ANY,  # we don't have any reference to this object
            'using': DEFAULT_DB_ALIAS,
            'verbosity': verbosity,
            'interactive': interactive,
            # following kwargs are not important for this test
            'stdout': mock.ANY,
            'plan': mock.ANY,
        }
        self.pre_migrate_receiver_mock.assert_called_once_with(
            **common_kwargs,
            signal=pre_migrate,
        )
        self.post_migrate_receiver_mock.assert_called_once_with(
            **common_kwargs,
            signal=post_migrate,
        )
