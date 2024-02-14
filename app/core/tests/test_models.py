"""
Tests for models.
"""

from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


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

    def test_create_recipe(self):
        """Test createing a recipe successful"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123"
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title="Test Recipe",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Test Description"
        )

        self.assertEqual(str(recipe), recipe.title)
        self.assertEqual(recipe.user.email, user.email)
        self.assertIsInstance(recipe.price, Decimal)

    def test_create_tag(self):
        """Test creating a new tag"""
        user = create_user()
        tag_name = "Test Tag"

        tag = models.Tag.objects.create(
            user=user,
            name=tag_name,
        )

        self.assertEqual(str(tag), tag_name)
        self.assertEqual(tag.user.id, user.id)

    def test_create_ingredient(self):
        """Test creating a new ingredient"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient 1"
        )

        self.assertEqual(str(ingredient), ingredient.name)
        self.assertEqual(ingredient.user.id, user.id)

    @patch("core.models.uuid.uuid4")
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test generatign image path"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
