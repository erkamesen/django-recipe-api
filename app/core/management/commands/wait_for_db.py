"""
Django command to wait for the database availability.
"""
from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Entry point for command.
        """

        self.stdout.write("Waiting for database.")
        db_up = False

        while not db_up:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable waiting 3 second.")
                time.sleep(3)

        self.stdout.write(self.style.SUCCESS("DB is Available :)"))
