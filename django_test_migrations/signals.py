from contextlib import contextmanager
from typing import Any, Iterator, List, Tuple

from django.db.models.signals import post_migrate, pre_migrate
from typing_extensions import TypeAlias

_MutedSignals: TypeAlias = Iterator[
    Tuple[List[Any], List[Any]],  # type: ignore[misc]
]


@contextmanager
def mute_migrate_signals() -> MutedSignals:
    """Context manager to mute migration-related signals."""
    pre_migrate_receivers = pre_migrate.receivers
    post_migrate_receivers = post_migrate.receivers
    pre_migrate.receivers = []
    post_migrate.receivers = []
    yield pre_migrate_receivers, post_migrate_receivers
    pre_migrate.receivers = pre_migrate_receivers
    post_migrate.receivers = post_migrate_receivers
