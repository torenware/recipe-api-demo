from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Tests for the public User API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user from a valid payload"""
        payload = {
            'email': 'test1-valid@email.com',
            'password': 'testpass',
            'name': 'Test Name'
        }

        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure the created user looks like our payload:
        user = get_user_model().objects.get(**resp.data)
        self.assertTrue(user.check_password(payload['password']))

        # Make sure the password is *not* returned on the wire
        self.assertNotIn('password', resp.data)

    def test_user_exists(self):
        """Test to assure trying to create an existing user fails"""
        payload = {
            'email': 'test1-valid@email.com',
            'password': 'testpass'
        }
        create_user(**payload)

        resp = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that a validation of pw length > len(5) is enforced"""
        payload = {
            'email': 'test2-valid@email.com',
            'password': 'testpass'
        }
        create_user(**payload)
        resp = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # We test also to assure there is no such user:
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
