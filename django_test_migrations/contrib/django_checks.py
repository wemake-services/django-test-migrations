# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.core import checks

from django_test_migrations.autonames import CHECK_NAME, check_migration_names


class AutoNames(AppConfig):
    """
    Class to install this check into ``INSTALLED_APPS`` in ``django``.

    See:
        https://docs.djangoproject.com/en/3.0/ref/applications/

    """

    name = CHECK_NAME

    def ready(self):
        """That's how we register our check when apps are ready."""
        checks.register(checks.Tags.compatibility)(check_migration_names)
