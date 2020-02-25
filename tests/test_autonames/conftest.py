# -*- coding: utf-8 -*-

import pytest


@pytest.fixture()
def ignore_migration(settings):
    """We patch settings to ignore this one bad migration."""
    settings.DTM_IGNORED_MIGRATIONS = {
        ('main_app', '0004_auto_20191119_2125'),
    }
    return settings
