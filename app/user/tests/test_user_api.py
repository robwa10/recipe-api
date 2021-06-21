from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_USER_URL = reverse('user:token')
ME_URL = reverse('user:me')

SAFE_EMAIL = 'bill@bailey.com'
SAFE_PASSWORD = 'mysecretpassword'
SAFE_NAME = 'Bill Bailey'


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_payload(
        email=SAFE_EMAIL,
        password=SAFE_PASSWORD,
        name=SAFE_NAME
        ):
    return {
        'email': email,
        'password': password,
        'name': name
    }


class PublicUserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user with a valid payload is successful"""
        payload = create_payload()
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertNotIn('password', res.data)
        self.assertTrue(user.check_password(payload['password']))

    def test_user_exists(self):
        payload = create_payload()
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = create_payload(password='abc')
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = create_payload()
        create_user(**payload)
        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test token is not created for invalid credentials"""
        create_user(**create_payload())
        payload = create_payload(password='bummer')
        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = create_payload()
        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(
            TOKEN_USER_URL,
            {'email': 'one', 'password': ''}
            )
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthenticated(self):
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API requests for the authenticated user"""

    def setUp(self):
        payload = create_payload()
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': SAFE_NAME,
            'email': SAFE_EMAIL
        })

    def test_post_me_not_allowed(self):
        """Test that user/me POST requests are not allowed"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_name(self):
        payload = create_payload(name='Bob Barker')
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(self.user.name, payload['name'])

    def test_update_user_password(self):
        payload = create_payload(password='ultimatepassword')
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
