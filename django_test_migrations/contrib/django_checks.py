from django.apps import AppConfig
from django.core import checks

from django_test_migrations.autonames import CHECK_NAME, check_migration_names


class AutoNames(AppConfig):
    """
    Class to install this check into ``INSTALLED_APPS`` in ``django``.

    If you have migrations that cannot be renamed,
    use ``DTM_IGNORED_MIGRATIONS`` setting in ``django.conf``
    to ignore ones you have to deal with:

    .. code:: python

        # settings.py
        DTM_IGNORED_MIGRATIONS = {
            ('main_app', '0004_auto_20191119_2125'),
            ('dependency_app', '0001_auto_20201110_2100'),
        }

    To run checks use:

    .. code:: bash

        python manage.py check --deploy --fail-level WARNING

    It will return exit code ``1`` if any violations are found.
    This can be easily added into your CI.

    See:
        https://docs.djangoproject.com/en/3.0/ref/applications/
        https://twitter.com/AdamChainz/status/1231895529686208512

    """

    #: Part of Django API.
    name = CHECK_NAME

    def ready(self):
        """That's how we register our check when apps are ready."""
        checks.register(checks.Tags.compatibility)(check_migration_names)
