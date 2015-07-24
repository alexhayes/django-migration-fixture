django-migration-fixture
========================

Easily use fixtures in Django 1.7+ data migrations.

The app also contains a management command to automatically convert 
:code:`initial_data.*` into migrations.

Prior to Django 1.7 :code:`initial_data.*` files where automatically run when the 
management command :code:`sync_db` was run, however this behaviour was 
discontinued in Django 1.7. Thus, this app is useful if you rely on this 
behaviour.

Essentially it leaves the :code:`initial_data.*` file in place and generates a 
data migration - as outlined 
`in the docs <http://django.readthedocs.org/en/1.7.x/topics/migrations.html#data-migrations>`_.

Install
-------

.. code-block:: python

	pip install django-migration-fixture

Then add :code:`django_migration_fixture` to your :code:`INSTALLED_APPS`.

.. code-block:: python

	INSTALLED_APPS += (
		'django_migration_fixture',
	)

Usage
-----

To automatically change your old-skool :code:`initial_data.*` files the simplest 
method is to simply call the :code:`create_initial_data_fixtures` management 
command.

.. code-block:: bash

	./manage.py create_initial_data_fixtures

The management command will automatically look for :code:`initial_data.*` files 
in your list of :code:`INSTALLED_APPS` and for each file found creates a data 
migration, similar to the following; 

.. code-block:: python

	# -*- coding: utf-8 -*-
	from __future__ import unicode_literals
	from django.db import models, migrations
	from django_migration_fixture import fixture
	import myapp
	
	class Migration(migrations.Migration):
	
		operations = [
			migrations.RunPython(**fixture(myapp, 'initial_data.yaml'))
		]

From this point it's just a matter of running `migrate` to apply your data 
migrations.

Note that this solution also supports rolling back your migration by deleting 
using primary key. If your migration should not be reversible then you can pass 
`reversible=False` to `fixture()`.

You can use this app for any fixtures, they don't have to be your initial_data 
files. Simply create a empty migration and add a call to 
:code:`migrations.RunPython(**fixture(myapp, 'foo.yaml'))`.

API Documentation
-----------------

:code:`fixture(app, fixtures, fixtures_dir='fixtures', raise_does_not_exist=False, reversible=True)`

- *app* is a Django app that contains your fixtures
- *fixtures* can take either a string or a list of fixture files. The extension 
  is used as the format supplied to :code:`django.core.serializers.deserialize`
- *fixtures_dir* is the directory inside your app that contains the fixtures
- *ignore_does_not_exist* - if set to True then 
  :code:`django_migration_fixture.FixtureObjectDoesNotExist` is raised if when 
  attempting a rollback the object in the fixture does not exist.
- *reversible* - if set to :code:`False` then any attempt to reverse the 
  migration will raise :code:`django.db.migrations.migration.IrreversibleError`.

Essentially :code:`fixture()` returns a dict containing the keys :code:`code` 
and :code:`reverse_code` which attempt to apply your fixture and rollback your 
fixture, respectively.

Inspiration
-----------

While attempting to migrate a large Django project to 1.7 I came across an issue 
which caused me to create Django `ticket 24023 <https://code.djangoproject.com/ticket/24023#ticket>`_. 

The project has a lot of fixtures that ensure a baseline state and converting 
them to code isn't really ideal, thus this project.

That issue has since been closed as a duplicate of 
`ticket 23699 <https://code.djangoproject.com/ticket/23699>`_ which itself has 
been closed and released in Django 1.7.2.

Needless to say, you may still need to create data migrations for fixtures 
regardless of the issue I came across.

Author
------

Alex Hayes <alex@alution.com>
