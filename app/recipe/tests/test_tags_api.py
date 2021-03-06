from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicApiTests(TestCase):
    """Test the non-authenticated Tag API calls"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to retrieve tags"""
        resp = self.client.get(TAGS_URL)
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

    def test_retrieve_tags(self):
        """Test that we get back tags we create"""
        Tag.objects.create(user=self.user, name="Vegetarian")
        Tag.objects.create(user=self.user, name="Entre")

        resp = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_tags_limited_to_current_user(self):
        """Make sure we only get the logged in user tags"""
        # Create another user, and create tags for it
        other_user = create_user(
            email='test@other.org', password='canna guess')
        Tag.objects.create(user=other_user, name='Snacks')
        Tag.objects.create(user=other_user, name='Snakes')

        # And a tag for our own default user
        Tag.objects.create(user=self.user, name='Tapas')

        resp = self.client.get(TAGS_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "Tapas")

    def test_create_tag_success(self):
        """Create a tag with valid input"""
        payload = {
            'name': 'Indian'
        }
        resp = self.client.post(TAGS_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(created)

    def test_create_tag_invalid(self):
        """Creation of tag should fail if input is invalid"""
        payload = {'name': ''}
        resp = self.client.post(TAGS_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=2.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
