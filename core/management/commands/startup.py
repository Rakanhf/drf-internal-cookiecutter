from django.core.management.base import BaseCommand
# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from django.core.management import call_command


class Command(BaseCommand):
    help = 'Runs the startup sequence: wait for db, makemigrations, migrate, migrate_user'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Starting startup sequence...'))

        # Wait for the database to be ready
        call_command('wait_for_db')

        # Make migrations
        call_command('makemigrations', '--no-input')

        # Apply migrations
        call_command('migrate')

        # Custom migrate_user command
        call_command('loadfakedata')

        self.stdout.write(self.style.SUCCESS('Startup sequence completed.'))