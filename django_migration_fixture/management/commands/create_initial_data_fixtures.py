try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import glob
import os
import re

from django.apps import apps
from django.core import management
from django.core.management import BaseCommand
from django.core.management.base import CommandError
from django.db.migrations import writer


class Command(BaseCommand):
    help = "Locate initial_data.* files and create data migrations for them."

    def handle(self, *args, **options):
        # Loop through all apps
        for app in apps.get_app_configs():
            # Look for initial_data.* files
            for fixture_path in glob.glob(os.path.join(app.path, 'fixtures', 'initial_data.*')):
                # Ensure the app has at least an initial migration
                if not glob.glob(os.path.join(app.path, 'migrations', '0001*')):
                    self.stdout.write(self.style.MIGRATE_HEADING("Migrations for '%s':" % app.label) + "\n")
                    self.stdout.write("  %s\n" % (self.style.WARNING("Ignoring '%s' - not migrated." % os.path.basename(fixture_path)),))
                    continue

                if self.migration_exists(app, fixture_path):
                    self.stdout.write(self.style.MIGRATE_HEADING("Migrations for '%s':" % app.label) + "\n")
                    self.stdout.write("  %s\n" % (self.style.NOTICE("Ignoring '%s' - migration already exists." % os.path.basename(fixture_path)),))
                    continue

                # Finally create our data migration
                self.create_migration(app, fixture_path)

    def monkey_patch_migration_template(self, app, fixture_path):
        """
        Monkey patch the django.db.migrations.writer.MIGRATION_TEMPLATE

        Monkey patching django.db.migrations.writer.MIGRATION_TEMPLATE means that we 
        don't have to do any complex regex or reflection.

        It's hacky... but works atm.
        """
        self._MIGRATION_TEMPLATE = writer.MIGRATION_TEMPLATE
        module_split = app.module.__name__.split('.')

        if len(module_split) == 1:
            module_import = "import %s\n" % module_split[0]
        else:
            module_import = "from %s import %s\n" % (
                '.'.join(module_split[:-1]),
                module_split[-1:][0],
            )

        writer.MIGRATION_TEMPLATE = writer.MIGRATION_TEMPLATE\
            .replace(
                '%(imports)s',
                "%(imports)s" + "\nfrom django_migration_fixture import fixture\n%s" % module_import
            )\
            .replace(
                '%(operations)s', 
                "        migrations.RunPython(**fixture(%s, ['%s'])),\n" % (
                    app.label,
                    os.path.basename(fixture_path)
                ) + "%(operations)s\n" 
            )

    def restore_migration_template(self):
        """
        Restore the migration template.
        """
        writer.MIGRATION_TEMPLATE = self._MIGRATION_TEMPLATE

    def migration_exists(self, app, fixture_path):
        """
        Return true if it looks like a migration already exists.
        """
        base_name = os.path.basename(fixture_path)
        # Loop through all migrations
        for migration_path in glob.glob(os.path.join(app.path, 'migrations', '*.py')):
            if base_name in open(migration_path).read():
                return True
        return False

    def create_migration(self, app, fixture_path):
        """
        Create a data migration for app that uses fixture_path.
        """
        self.monkey_patch_migration_template(app, fixture_path)

        out = StringIO()
        management.call_command('makemigrations', app.label, empty=True, stdout=out)

        self.restore_migration_template()

        self.stdout.write(out.getvalue())
