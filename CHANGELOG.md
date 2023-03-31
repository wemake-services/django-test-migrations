# Version history

We follow Semantic Versions since the `0.1.0` release.

## Version 1.3.0

- Adds Python 3.11 support
- Drops Python 3.7 support
- Adds Django 4.1 support
- Drops Django 2.2 support


## Version 1.2.0

### Features

- Adds Python 3.10
- Adds Django 4.0 support
- Updates `typing_extensions` to `>=3.6,<5`


## Version 1.1.0

### Features

- Adds Django 3.1 support (#123, #154)
- Adds markers/tags to migration tests (#138)
- Adds database configuration checks (#91)

### Bugfixes

- Fixes tables dropping on MySQL by disabling foreign keys checks (#149)
- Fixes migrate signals muting when running migrations tests (#133)

### Misc

- Runs tests against PostgreSQL and MySQL database engines (#129)


## Version 1.0.0

### Breaking Changes

- Rename following `Migrator` methods (#83):

  + `before` to `apply_initial_migration`
  + `after` to `apply_tested_migration`

- Improves databases setup and teardown for migrations tests (#76)
  Currently `Migrator.reset` uses `migrate` management command and all logic
  related to migrations tests setup is moved to
  `Migrator.apply_tested_migration`.

### Bugfixes

- Fixes `pre_migrate` and `post_migrate` signals muting (#87)
- Adds missing `typing_extension` dependency (#86)

### Misc

- Refactor tests (#79)
- Return `django` installed from `master` branch to testing matrix (#77)


## Version 0.3.0

### Features

- Drops `django@2.1` support
- Adds `'*'` alias for ignoring
  all migrations in an app with `DTM_IGNORED_MIGRATIONS`

### Bugfixes

- Fixes how `pre_migrate` and `post_migrate` signals are muted

### Misc

- Updates `wemake-python-styleguide`
- Moves from `travis` to Github Actions


## Version 0.2.0

### Features

- Adds `autoname` check to forbid `*_auto_*` named migrations
- Adds `django@3.0` support
- Adds `python3.8` support


### Bugfixes

- Fixes that migtaions were failing with `pre_migrate` and `post_migrate` signals
- Fixes that tests were failing when `pytest --nomigration` was executed,
  now they are skipped


### Misc

- Updates to `poetry@1.0`


## Version 0.1.0

- Initial release
