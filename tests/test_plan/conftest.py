import pytest
from django.db.migrations import Migration


@pytest.fixture
def plan():
    """Fake migrations plan for testing purposes."""
    migrations_plan = [
        Migration('0001_initial', 'app1'),
        Migration('0002_second', 'app1'),
        Migration('0001_initial', 'app2'),
        Migration('0003_third', 'app1'),
        Migration('0004_fourth', 'app1'),
        Migration('0002_second', 'app2'),
        Migration('0005_fifth', 'app1'),
        Migration('0001_initial', 'app3'),
        Migration('0006_sixth', 'app1'),
    ]
    return [(migration, False) for migration in migrations_plan]
