from django.core.management.base import BaseCommand
from django.db import connections
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for database.")

        while True:
            try:
                connections['default'].ensure_connection()
                break
            except Exception as e:
                self.stdout.write(
                    f"Database unavailable, waiting 3 second. Error: {e}")
                time.sleep(3)

        self.stdout.write(self.style.SUCCESS("DB is Available :)"))
