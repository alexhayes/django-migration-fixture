# django-migration-fixture

App to easily turn initial_data.* fixtures into Django 1.7 data migrations.

This is useful if you have a legacy project you are migration to Django 1.7+ which contains initial_data.* files that you rely upon.

Essentially it leaves the initial_data.* file in place and generates a data migration - as outlined [in the docs](http://django.readthedocs.org/en/1.7.x/topics/migrations.html#data-migrations).

## Install

```bash
pip install git+https://github.com/alexhayes/django-migration-fixture.git
```

Then add `django_migration_fixture` to your INSTALLED_APPS.

```python
INSTALLED_APPS += (
	'django_migration_fixture',
)
```

## Usage

Simplest method is to simply call the `create_initial_data_fixtures` management command.

```bash
./manage.py create_initial_data_fixtures
```

The management command will automatically look for `initial_data.*` files in your list of INSTALLED_APPS and for each file found creates a data migration, similar to the following; 

```python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from django_migration_fixture import fixture
import myapp

class Migration(migrations.Migration):

	operations = [
		migrations.RunPython(**fixture(myapp, 'initial_data.yaml'))
	]
```

From this point it's just a matter of running `migrate` to apply your data migrations.

Note that this solution also supports rolling back your migration (by deleting using primary key) - thus if you don't want your data removed when doing a rollback you should fake.  

## API

`fixture(app, fixtures, fixtures_dir='fixtures', raise_does_not_exist=False)`

- *app* is a Django app that contains your fixtures
- *fixtures* can take either a string or a list of fixture files. The extension is used as the format supplied to `django.core.serializers.deserialize`
- *fixtures_dir* is the directory inside your app that contains the fixtures
- *ignore_does_not_exist* if set to True then `django_migration_fixture.FixtureObjectDoesNotExist` is raised if when attempting a rollback the object in the fixture does not exist.

Essentially `fixture()` returns a dict containing the keys 'code' and 'reverse_code' which attempt to apply your fixture and rollback your fixture, respectively.

## Inspiration

While attempting to migrate a large Django project to 1.7 I came across an issue which caused me to create Django [ticket 24023](https://code.djangoproject.com/ticket/24023#ticket). 

The project has a lot of fixtures that ensure a baseline state and converting them to code isn't really ideal, thus this project.

That issue has since been closed as a duplicate of [ticket 23699](https://code.djangoproject.com/ticket/23699) which itself has been closed and released in Django 1.7.2.

Needless to say, you may still need to create data migrations for your initial_data.* files, regardless of the issue I came across.

## Author

Alex Hayes <alex@alution.com>