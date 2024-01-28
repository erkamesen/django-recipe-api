"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_succesfull(self):
        """
        Test create user with email succesfully
        """
        email = "test@example.com"
        password = "supersecretkey"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test new user email normalize"""

        TEST_EMAILS = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in TEST_EMAILS:
            user = get_user_model().objects.create_user(email)
            self.assertEqual(user.email, expected)

    def test_new_user_has_email_or_raise_error(self):
        """Test creating user has email or throw ValueError"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "testpass123")

    def test_create_super_user(self):
        """Test create a super user"""
        email = "test@example.com"
        password = "superuserpassword"
        user = get_user_model().objects.create_superuser(email, password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
