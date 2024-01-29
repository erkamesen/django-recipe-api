"""
Test for the user api
URLS:
    - http://127.0.0.1/api/recipes/ Create - List
    - http://127.0.0.1/api/recipes/<int:id>/ Retrieve - Update - Delete
# Public Tests: Unauthenticated requests
# Private Tests: Authenticated requests
"""

from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from decimal import Decimal

from core.models import Recipe

from recipe.api.serializers import RecipeSerializer, RecipeDetailSerializer
from django.db.utils import IntegrityError

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Create and return a decipe detail URL."""
    return reverse("recipe:recipe-detail", args=[recipe_id, ])


def create_recipe(user, **kwargs):
    """Create and return a sample recipe."""
    defaults = {
        "title": "Test Title",
        "time_minutes": 5,
        "price": Decimal("2.99"),
        "description": "Test Description",
        "link": "http://example.com/recipe.pdf"
    }

    defaults.update(kwargs)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**kwargs):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**kwargs)


class PublicRecipeAPITests(TestCase):
    """Test APIs that not required authenticate"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required API"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_create(self):
        """Test auth is required Create API"""

        with self.assertRaises(IntegrityError):
            recipe = {
                "title": "Test Title",
                "time_minutes": 5,
                "price": Decimal("2.99"),
                "description": "Test Description",
                "link": "http://example.com/recipe/2"
            }
            Recipe.objects.create(**recipe)


class PrivateRecipeAPITests(TestCase):
    """Test APIs that required authenticate"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com",
                                password="testpass123",)

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieve recipes API"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(recipes), 3)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(
            email="test2@example.com", password="testpass123")

        create_recipe(user=other_user)
        create_recipe(user=other_user)
        create_recipe(user=other_user)
        create_recipe(user=other_user)
        create_recipe(user=other_user)

        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(recipes), 1)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):  #  POST
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data.get("id"))
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):  #  PATCH
        """Test partial update of a recipe."""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="Test",
            link=original_link
        )

        payload = {
            "title": "New Test",
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload.get("title"))
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):  # PUT
        """Test full update of recipe with PUT request"""
        recipe = create_recipe(
            user=self.user,
        )

        payload = {
            "title": "New Title",
            "link": "http://testlink.com",
            "description": "New Description",
            "time_minutes": 2,
            "price": Decimal("3.33"),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):  #  PATCH USER
        """Test changing the recipe user results in an error"""
        new_user = create_user(email="uesr2@example.com",
                               password="testpass123")
        recipe = create_recipe(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):  #  DELETE
        """Test deleting a recipe successful"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe"""
        new_user = create_user(email="test2@example.com",
                               password="testpass123")
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
