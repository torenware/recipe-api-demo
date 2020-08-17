from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return the recipe's URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='You are it'):
    """Create a test tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Paprika'):
    """Create an ingredient object"""
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        resp = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(resp.data, serializer.data)

    def test_create_simple_recipe(self):
        """Test creating a recipe via API"""
        payload = {
            'title': 'NY Cheesecake',
            'time_minutes': 30,
            'price': 5.00,
        }
        resp = self.client.post(RECIPE_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Kosher')
        tag2 = sample_tag(user=self.user, name='Milchik')
        payload = {
            'title': 'Kugle',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 25,
            'price': 5.00
        }
        resp = self.client.post(RECIPE_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])

        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Create recipe with ingredients"""
        ingred1 = sample_ingredient(user=self.user, name='offal')
        ingred2 = sample_ingredient(user=self.user, name='achiote')
        payload = {
            'title': "Menudo",
            'time_minutes': 90,
            'price': 8.00,
            'ingredients': [ingred1.id, ingred2.id]
        }
        resp = self.client.post(RECIPE_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])

        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingred1, ingredients)
        self.assertIn(ingred2, ingredients)
