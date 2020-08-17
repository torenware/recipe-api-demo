from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from django.core.exceptions import ValidationError


def sample_user(email="test@myuser.org", password="not so secret"):
    """Test user for model tests"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email"""
        email = 'test@django-course.com'
        password = "Some password"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalized(self):
        email = "test@DJANGO-COURSE.COM"
        password = "Some password"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, "test@django-course.com")

    def test_user_has_email(self):
        """Test if lacking an email throws an exception"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_email_must_be_valid(self):
        """New user must be passed syntactically valid email"""

        email = 'not an email'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(email, 'test123')

    def test_admin_user_creates(self):
        """Test creation of an admin user"""

        user = get_user_model().objects.create_superuser(
            "super@user.com",
            "pass-a-woid"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test creation of a tag and its str rep"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test creation of an ingredient and its str rep"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Salami'
        )
        self.assertEqual(str(ingredient), ingredient.name)
