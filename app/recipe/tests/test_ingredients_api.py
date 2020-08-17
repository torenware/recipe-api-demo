from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicApiTests(TestCase):
    """Test the non-authenticated Ingredient API calls"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to retrieve ingredients"""
        resp = self.client.get(INGREDIENT_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests that require an authenticated user"""

    def setUp(self):
        self.client = APIClient()

        # Create our test user
        payload = {
            'email': 'killroy@washere.org',
            'password': 'long-enough',
            'name': 'Killroy',
        }

        self.user = create_user(**payload)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test that we get back ingredients we create"""
        Ingredient.objects.create(user=self.user, name="Dal")
        Ingredient.objects.create(user=self.user, name="Hot sauce")

        resp = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_ingredients_limited_to_current_user(self):
        """Make sure we only get the logged in user ingredients"""
        # Create another user, and create ingredients for it
        other_user = create_user(
            email='test@other.org', password='canna guess')
        Ingredient.objects.create(user=other_user, name='Snakes')

        # And a ingredient for our own default user
        Ingredient.objects.create(user=self.user, name='Talapia')

        resp = self.client.get(INGREDIENT_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "Talapia")

    def test_create_ingredient_success(self):
        """Create a ingredient with valid input"""
        payload = {
            'name': 'Achiote paste'
        }
        resp = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(created)

    def test_create_ingredient_invalid(self):
        """Creation of ingredient should fail if input is invalid"""
        payload = {'name': ''}
        resp = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
