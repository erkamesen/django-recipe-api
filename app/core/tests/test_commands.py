"""
Command Tests
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_check):
        """
        Test waiting for database if ready.
        """
        # Mocked `check` method will return True
        patched_check.return_value = True

        # Call the `wait_for_db` management command
        call_command("wait_for_db")

        # Assert that the `check` method is called once with the correct parameters
        patched_check.assert_called_once_with(databases=["default"])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for database when getting OperationalError
        """

        # Set up side effects for the `check` method
        patched_check.side_effect = [
            Psycopg2OpError] * 2 + [OperationalError] * 3 + [True]

        # Call the `wait_for_db` management command
        call_command("wait_for_db")

        # Assert that the `check` method is called a total of 6 times
        self.assertEqual(patched_check.call_count, 6)
        # Assert that the `check` method is called with the correct parameters
        patched_check.assert_called_with(databases=["default"])
