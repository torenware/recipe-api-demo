from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create a sample recipe"""
    defaults = {
        'title': 'Butterbeer',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthorized access to recipe api"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test if we get a 401 on unauthenticated access"""
        resp = self.client.get(RECIPE_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Tests that require an authenticated user"""

    def setUp(self):
        self.client = APIClient()

        # Create our test user
        payload = {
            'email': 'killroy@washere.org',
            'password': 'long-enough',
            'name': 'Killroy',
        }

        self.user = get_user_model().objects.create_user(**payload)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipe(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        resp = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipe_for_user_only(self):
        """Make sure we only see our own recipes"""
        other_user = get_user_model().objects.create_user(
            email='test@other.org', password='canna guess')
        sample_recipe(user=other_user)
        sample_recipe(user=self.user)

        resp = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data, serializer.data)
