# Version history

We follow Semantic Versions since the `0.1.0` release.


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
