import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until DB is avaliable."""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for DB to be available...')
        db_connection = None
        while not db_connection:
            try:
                db_connection = connections['default']
            except OperationalError:
                self.stdout.write(
                    'DB unavailable, waiting 1 second before retrying.'
                )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available.'))
