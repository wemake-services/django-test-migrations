import subprocess


def test_managepy_check():
    """Checks that checks do fail."""
    proc = subprocess.Popen(
        [
            'python',
            'django_test_app/manage.py',
            'check',
            '--fail-level',
            'WARNING',
        ],
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf8',
    )

    proc.communicate()
    assert proc.returncode == 1
