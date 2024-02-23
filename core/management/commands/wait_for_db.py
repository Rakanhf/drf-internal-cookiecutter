# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    help = "Waits for the database to be ready"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        retry_count = 0
        while not db_conn and retry_count < 15:  # Retry up to 15 times
            try:
                db_conn = connections["default"]
                db_conn.cursor()
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 2 seconds...")
                time.sleep(2)  # Wait for 5 seconds before retrying
                retry_count += 1
        if not db_conn:
            self.stdout.write(
                self.style.ERROR("Database not available after multiple retries.")
            )
            return
        db_conn.close()
        self.stdout.write(self.style.SUCCESS("Database available!"))
