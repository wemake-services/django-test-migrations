# django-test-migrations

[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services)
[![Build Status](https://travis-ci.com/wemake-services/django-test-migrations.svg?branch=master)](https://travis-ci.com/wemake-services/django-test-migrations)
[![Coverage](https://coveralls.io/repos/github/wemake-services/django-test-migrations/badge.svg?branch=master)](https://coveralls.io/github/wemake-services/django-test-migrations?branch=master)
[![Python Version](https://img.shields.io/pypi/pyversions/django-test-migrations.svg)](https://pypi.org/project/django-test-migrations/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)


## Features

- Allows to test `django` schema and data migrations
- Allows to test both forward and rollback migrations
- Allows to test the migrations order
- Fully typed with annotations and checked with `mypy`, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Easy to start: has lots of docs, tests, and tutorials


## Installation

```bash
pip install django-test-migrations
```

We support several `django` versions:

- `1.11`
- `2.1`
- `2.2`

Other versions might work too, but they are not officially supported.


## Testing django migrations

Testing migrations is not a frequent thing in `django` land.
But, sometimes it is totally required. When?

When we do complex schema or data changes
and what to be sure that existing data won't be corrupted.
We might also want to be sure that all migrations can be safely rolled back.
And as a final touch we want to be sure that migrations
are in the correct order and have correct dependencies.

### Testing forward migrations

To test all migrations we have a [`Migrator`](https://github.com/wemake-services/django-test-migrations/blob/master/django_test_migrations/migrator.py) class.

It has three methods to work with:

- `.before()` which takes app and migration names to generate a state
  before the actual migration happens
- `.after()` which takes app and migration names to perform the actual migration
- `.reset()` to clean everything up after we are done with testing

So, here's an example:

```python
from django_test_migrations.migrator import Migrator

migrator = Migrator(database='default')

# Initial migration, currently our model has only a single string field:
old_state = migrator.before(('main_app', '0001_initial'))
SomeItem = old_state.apps.get_model('main_app', 'SomeItem')

# Let's create a model with just a single field specified:
SomeItem.objects.create(string_field='a')
assert len(SomeItem._meta.get_fields()) == 2  # id + string_field

# Now this migration will add `is_clean` field to the model:
new_state = migrator.after(('main_app', '0002_someitem_is_clean'))
SomeItem = new_state.apps.get_model('main_app', 'SomeItem')

# We can now test how our migration worked, new field is there:
assert SomeItem.objects.filter(is_clean=True).count() == 0
assert len(SomeItem._meta.get_fields()) == 3  # id + string_field + is_clean

# Cleanup:
migrator.reset()
```

That was an example of a forward migration.

### Backward migration

The thing is that you can also test backward migrations.
Nothing really changes except migration names that you pass and your logic:

```python
migrator = Migrator()

# Currently our model has two field, but we need a rollback:
old_state = migrator.before(('main_app', '0002_someitem_is_clean'))
SomeItem = old_state.apps.get_model('main_app', 'SomeItem')

# Create some data to illustrate your cases:
# ...

# Now this migration will drop `is_clean` field:
new_state = migrator.after(('main_app', '0001_initial'))

# Assert the results:
# ...

# Cleanup:
migrator.reset()
```

### Testing migrations ordering

Sometimes we also want to be sure that our migrations are in the correct order.
And all our `dependecies = [...]` are correct.

To achieve that we have [`plan.py`](https://github.com/wemake-services/django-test-migrations/blob/master/django_test_migrations/plan.py) module.

That's how it can be used:

```python
from django_test_migrations.plan import all_migrations, nodes_to_tuples

main_migrations = all_migrations('default', ['main_app', 'other_app'])
assert nodes_to_tuples(main_migrations) == [
    ('main_app', '0001_initial'),
    ('main_app', '0002_someitem_is_clean'),
    ('other_app', '0001_initial'),
    ('main_app', '0003_auto_20191119_2125'),
    ('main_app', '0004_auto_20191119_2125'),
    ('other_app', '0002_auto_20191120_2230'),
]
```

This way you can be sure that migrations
and apps that depend on each other will be executed in the correct order.


## Test framework integrations

We support several test frameworks as first-class citizens.
That's a testing tool after all!

### pytest

We ship `django-test-migrations` with a `pytest` plugin
that provides two convinient fixtures:

- `migrator_factory` that gives you an opportunity
  to create `Migrator` classes for any database
- `migrator` instance for the `'default'` database

That's how it can be used:

```python
import pytest

@pytest.mark.django_db
def test_pytest_plugin_initial(migrator):
    """Ensures that the initial migration works."""
    old_state = migrator.before(('main_app', None))

    with pytest.raises(LookupError):
        # Models does not yet exist:
        old_state.apps.get_model('main_app', 'SomeItem')

    new_state = migrator.after(('main_app', '0001_initial'))
    # After the initial migration is done, we can use the model state:
    SomeItem = new_state.apps.get_model('main_app', 'SomeItem')
    assert SomeItem.objects.filter(string_field='').count() == 0
```

### unittest

We also ship an integration with the built-in `unittest` framework.

Here's how it can be used:

```python
from django_test_migrations.contrib.unittest_case import MigratorTestCase

class TestDirectMigration(MigratorTestCase):
    """This class is used to test direct migrations."""

    migrate_from = ('main_app', '0002_someitem_is_clean')
    migrate_to = ('main_app', '0003_auto_20191119_2125')

    def prepare(self):
        """Prepare some data before the migration."""
        SomeItem = self.old_state.apps.get_model('main_app', 'SomeItem')
        SomeItem.objects.create(string_field='a')
        SomeItem.objects.create(string_field='a b')

    def test_migration_main0003(self):
        """Run the test itself."""
        SomeItem = self.new_state.apps.get_model('main_app', 'SomeItem')

        assert SomeItem.objects.count() == 2
        assert SomeItem.objects.filter(is_clean=True).count() == 1
```


## Credits

This project is based on work of other awesome people:

- [@asfaltboy](https://gist.github.com/asfaltboy/b3e6f9b5d95af8ba2cc46f2ba6eae5e2)
- [@blueyed](https://gist.github.com/blueyed/4fb0a807104551f103e6#gistcomment-1546191)

## License

MIT.
