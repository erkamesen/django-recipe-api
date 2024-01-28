"""
Tests for the django admin
URLS FOR ADMIN<: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#admin-reverse-urls
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminTest(TestCase):
    """Tests for admin"""

    def setUp(self):
        """Create Client & Super User & Normal User"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="superpass123",
        )
        # with force_login() you can simulate a login withouh token or etc.
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="normalpass123",
            name="Test User",
        )

    def test_users_list(self):
        """Test are users are listed on page"""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page"""
        """http://127.0.0.1:8000/admin/core/user/<int:id>/change/"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test for create user page"""
        """http://127.0.0.1:8000/admin/core/user/add/"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
