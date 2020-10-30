import re
import subprocess

from django_test_migrations.constants import MIGRATION_TEST_MARKER


def test_call_pytest_setup_plan():
    """Checks that module is registered and visible in the meta data."""
    output_text = subprocess.check_output(
        [
            'pytest',
            '--setup-plan',

            # We need this part because otherwise check fails with `1` code:
            '--cov-fail-under',
            '0',
        ],
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf8',
    )

    assert 'migrator' in output_text
    assert 'migrator_factory' in output_text


def test_pytest_registers_marker():
    """Ensure ``MIGRATION_TEST_MARKER`` marker is registered."""
    output_text = subprocess.check_output(
        ['pytest', '--markers'],
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf8',
    )

    assert MIGRATION_TEST_MARKER in output_text


def test_pytest_markers():
    """Ensure ``MIGRATION_TEST_MARKER`` markers are properly added."""
    output_text = subprocess.check_output(
        [
            'pytest',
            '--collect-only',

            # Collect only tests marked with ``MIGRATION_TEST_MARKER`` marker
            '-m',
            MIGRATION_TEST_MARKER,

            # We need this part because otherwise check fails with `1` code:
            '--cov-fail-under',
            '0',
        ],
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf8',
    )

    search_result = re.search(
        r'(?P<selected_number>\d+)\s+selected',
        output_text,
    )
    assert search_result
    assert int(search_result.group('selected_number') or 0) > 0
    assert 'test_pytest_plugin' in output_text
