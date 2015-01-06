import os
from django.core import serializers


class FixtureObjectDoesNotExist(Exception):
    """Raised when attempting to roll back a fixture and the instance can't be found"""
    pass


def fixture(app, fixtures, fixtures_dir='fixtures', raise_does_not_exist=False):
    """
    Load fixtures using a data migration.

    Usage:

    import myapp
    import anotherapp

    operations = [
        migrations.RunPython(**fixture(myapp, 'eggs.yaml')),
        migrations.RunPython(**fixture(anotherapp, ['sausage.json', 'walks.yaml']))
    ]
    """
    fixture_path = os.path.join(app.__path__[0], fixtures_dir)
    if isinstance(fixtures, basestring):
        fixtures = [fixtures]

    def get_format(fixture):
        return os.path.splitext(fixture)[1][1:]

    def get_objects():
        for fixture in fixtures:
            with open(os.path.join(fixture_path, fixture), 'rb') as f:
                objects = serializers.deserialize(get_format(fixture), f, ignorenonexistent=True)
                for obj in objects:
                    yield obj

    def load_fixture(apps, schema_editor):
        for obj in get_objects():
            obj.save()

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
                    raise FixtureObjectDoesNotExist("Model %s instance with kwargs %s does not exist." % (model, kwargs))

    return dict(code=load_fixture, reverse_code=unload_fixture)