"""
Test for the Ingredient api
URLS:
    - http://127.0.0.1/api/recipes/ Create - List
    - http://127.0.0.1/api/recipes/<int:id>/ Retrieve - Update - Delete
# Public Tests: Unauthenticated requests
# Private Tests: Authenticated requests
"""

from django.contrib.auth import get_user_model

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.api.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def create_user(email="user@example.com", password="testpass123"):
    """Create and return user"""
    user = get_user_model().objects.create_user(email=email, password=password)
    return user


def detail_url(ingredient_id):
    """Create and return detail URL for ingredient"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id, ])


class PublicIngredientsAPITests(TestCase):
    """Test unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrievening ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieve ingredients with authenticate"""
        Ingredient.objects.create(name="Test Ingredient", user=self.user)
        Ingredient.objects.create(name="Test Ingredient 2", user=self.user)

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test retrieve ingredients limited for current user"""
        other_user = create_user(
            email="user2@example.com", password="testpass123")
        Ingredient.objects.create(name="Test Ingredient", user=other_user)
        ingredient = Ingredient.objects.create(
            name="Test Ingredient 2", user=self.user)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get("name"), ingredient.name)
        self.assertEqual(res.data[0].get("id"), ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Test",
        )

        payload = {
            "name": "Test 2"
        }

        url = detail_url(ingredient.id)
        res = self.client.patch(url, data=payload)

        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("name"), payload.get("name"))

    def test_update_other_user_ingredient(self):
        """Test update for unauthorized update process"""
        other_user = create_user(
            email="user2@example.com", password="testpass123")

        ingredient = Ingredient.objects.create(
            user=other_user,
            name="Test 2",
        )

        url = detail_url(ingredient.id)
        payload = {
            "name": "Unauthorized Process Name"
        }
        res = self.client.patch(url, data=payload)

        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(ingredient.name, payload.get("name"))

    def test_delete_ingredient(self):
        """Test delete ingredient API"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Test",
        )

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        is_exist = Ingredient.objects.filter(
            user=self.user, name="Test").exists()
        self.assertFalse(is_exist)

    def test_delete_other_user_ingredient(self):
        """Test other users ingredient s delete"""

        other_user = create_user(
            email="user2@example.com", password="testpass123")

        ingredient = Ingredient.objects.create(
            user=other_user,
            name="Test 2",
        )
        url = detail_url(ingredient.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        is_exist = Ingredient.objects.filter(
            user=other_user, name="Test 2").exists()
        self.assertTrue(is_exist)
