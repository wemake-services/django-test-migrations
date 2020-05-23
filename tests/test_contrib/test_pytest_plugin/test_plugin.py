import subprocess


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
