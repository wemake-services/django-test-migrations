# -*- coding: utf-8 -*-

from fnmatch import fnmatch
from typing import FrozenSet, List, Tuple

from django.conf import settings
from django.core.checks import CheckMessage, Warning
from typing_extensions import Final

_IgnoreAppSpec = FrozenSet[str]

_IgnoreMigrationSpec = FrozenSet[Tuple[str, str]]

#: We use this type hint to represent ignore rules for migrations.
_IgnoreSpec = Tuple[_IgnoreAppSpec, _IgnoreMigrationSpec]

#: We use this value as a unique identifier of this check.
CHECK_NAME: Final = 'django_test_migrations.autonames'

#: Settings name for this check to ignore some migrations.
_SETTINGS_NAME: Final = 'DTM_IGNORED_MIGRATIONS'

# Special key to ignore all migrations inside an app
_IGNORE_APP_MIGRATIONS_SPECIAL_KEY: Final = '*'


def _is_ignored(
    app_label: str, migration_name: str, ignored: _IgnoreSpec,
) -> bool:
    ignored_apps, ignored_migrations = ignored

    return (
        app_label in ignored_apps or
        (app_label, migration_name) in ignored_migrations
    )


def _build_ignores() -> _IgnoreSpec:
    ignored_migrations: _IgnoreMigrationSpec = getattr(
        settings, _SETTINGS_NAME, frozenset(),
    )

    ignored_apps: _IgnoreAppSpec = frozenset(
        app_label
        for app_label, migration_name in ignored_migrations
        if migration_name == _IGNORE_APP_MIGRATIONS_SPECIAL_KEY
    )

    return ignored_apps, ignored_migrations


def check_migration_names(*args, **kwargs) -> List[CheckMessage]:
    """
    Finds automatic names in available migrations.

    We use nested import here, because some versions of django fails otherwise.
    They do raise:
    ``django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.``
    """
    from django.db.migrations.loader import MigrationLoader  # noqa: WPS433

    loader = MigrationLoader(None, ignore_no_migrations=True)
    loader.load_disk()

    messages = []
    ignores = _build_ignores()

    for app_label, migration_name in loader.disk_migrations.keys():
        if _is_ignored(app_label, migration_name, ignores):
            continue

        if fnmatch(migration_name, '????_auto_*'):
            messages.append(
                Warning(
                    'Migration {0}.{1} has an automatic name.'.format(
                        app_label, migration_name,
                    ),
                    hint=(
                        'Rename the migration to describe its contents, ' +
                        "or if it's from a third party app, add to " +
                        _SETTINGS_NAME
                    ),
                    id='{0}.E001'.format(CHECK_NAME),
                ),
            )
    return messages
