# -*- coding: utf-8 -*-
"""Easily use fixtures in Django 1.7+ data migrations."""
# :copyright: (c) 2015 Alex Hayes and individual contributors,
#                 All rights reserved.
# :license:   MIT License, see LICENSE for more details.

from collections import namedtuple

version_info_t = namedtuple(
    'version_info_t', ('major', 'minor', 'micro', 'releaselevel', 'serial'),
)

VERSION = version_info_t(0, 5, 1, '', '')
__version__ = '{0.major}.{0.minor}.{0.micro}{0.releaselevel}'.format(VERSION)
__author__ = 'Alex Hayes'
__contact__ = 'alex@alution.com'
__homepage__ = 'http://github.com/alexhayes/django-migration-fixture'
__docformat__ = 'restructuredtext'

# -eof meta-

from contextlib import contextmanager
import os
import django
from django.core import serializers
from six import string_types
from functools import wraps


class FixtureObjectDoesNotExist(Exception):
    """
    Raised if when attempting to roll back a fixture the instance can't be found
    """
    pass


def fixture(app, fixtures, fixtures_dir='fixtures', raise_does_not_exist=False,
            reversible=True, models=[]):
    """
    Load fixtures using a data migration.

    The migration will by default provide a rollback, deleting items by primary
    key. This is not always what you want ; you may set reversible=False to
    prevent rolling back.

    Usage:

    import myapp
    import anotherapp

    operations = [
        migrations.RunPython(**fixture(myapp, 'eggs.yaml')),
        migrations.RunPython(**fixture(anotherapp, ['sausage.json', 'walks.yaml']))
        migrations.RunPython(**fixture(yap, ['foo.json'], reversible=False))
    ]
    """
    fixture_path = os.path.join(app.__path__[0], fixtures_dir)
    if isinstance(fixtures, string_types):
        fixtures = [fixtures]

    def get_format(fixture):
        return os.path.splitext(fixture)[1][1:]

    def get_objects():
        for fixture in fixtures:
            with open(os.path.join(fixture_path, fixture), 'rb') as f:
                objects = serializers.deserialize(get_format(fixture),
                                                  f,
                                                  ignorenonexistent=True)
                for obj in objects:
                    yield obj

    def patch_apps(func):
        """
        Patch the app registry.

        Note that this is necessary so that the Deserializer does not use the
        current version of the model, which may not necessarily be representative
        of the model the fixture was created for.
        """
        @wraps(func)
        def inner(apps, schema_editor):
            try:
                # Firstly patch the serializers registry
                original_apps = django.core.serializers.python.apps
                django.core.serializers.python.apps = apps
                return func(apps, schema_editor)

            finally:
                # Ensure we always unpatch the serializers registry
                django.core.serializers.python.apps = original_apps

        return inner

    @patch_apps
    def load_fixture(apps, schema_editor):
        for obj in get_objects():
            obj.save()

    @patch_apps
    def unload_fixture(apps, schema_editor):
        for obj in get_objects():
            model = apps.get_model(app.__name__, obj.object.__class__.__name__)
            kwargs = dict()
            if 'id' in obj.object.__dict__:
                kwargs.update(id=obj.object.__dict__.get('id'))
            elif 'slug' in obj.object.__dict__:
                kwargs.update(slug=obj.object.__dict__.get('slug'))
            else:
                kwargs.update(**obj.object.__dict__)
            try:
                model.objects.get(**kwargs).delete()
            except model.DoesNotExist:
                if not raise_does_not_exist:
                    raise FixtureObjectDoesNotExist(("Model %s instance with "
                                                     "kwargs %s does not exist."
                                                     % (model, kwargs)))

    kwargs = dict(code=load_fixture)

    if reversible:
        kwargs['reverse_code'] = unload_fixture

    return kwargs
