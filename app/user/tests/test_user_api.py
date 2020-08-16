from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


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
            'password': 'testpass',
            'name': 'Gotta Havit'
        }
        create_user(**payload)

        resp = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {'email': 'test@londonappdev.com',
                   'password': 'pw', 'user': "Frodrick"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test token creation API for an existing user"""
        payload = {
            'email': 'killroy@washere.org',
            'password': 'long-enough',
            # 'name': 'Killroy',
        }

        # User needs to exist for this test, so create it:
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_req_token_invalid_credential(self):
        """Test to insure a bad credential yields no token"""

        # User but different creds
        create_user(email='killroy@washere.org',
                    password='Completely different')

        payload = {
            'email': 'killroy@washere.org',
            'password': 'long-enough',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_req_token_invalid_no_user(self):
        """Test token will be denied if the user does not exist"""

        payload = {
            'email': 'killroy@washere.org',
            'password': 'long-enough',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_missing_field_no_token(self):
        """Make sure email and password are required"""
        res = self.client.post(
            TOKEN_URL, {'email': 'not-email', 'password': ''})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
