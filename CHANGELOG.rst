CHANGELOG
=========

0.5.0
-----

- Ensured that the app registry used for deserialization is that provided by the
  migration, not the current app registry which may not match the current state
  of the database or the fixture itself.
- Changed README to rst format.
- Refactor setup.py.

0.4.0
-----

- Python 3 support
- Support non reversible migrations

