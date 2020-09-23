from contextlib import contextmanager

from django.db.models.signals import post_migrate, pre_migrate


@contextmanager
def mute_migrate_signals():
    pre_migrate_receivers = pre_migrate.receivers
    post_migrate_receivers = post_migrate.receivers
    pre_migrate.receivers = post_migrate.receivers = []
    yield pre_migrate_receivers, post_migrate_receivers
    pre_migrate.receivers = pre_migrate_receivers
    post_migrate.receivers = post_migrate_receivers
