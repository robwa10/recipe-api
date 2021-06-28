from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


SAFE_EMAIL = 'test@email.com'
SAFE_PASSWORD = 'test123'


def create_sample_user(email=SAFE_EMAIL, password=SAFE_PASSWORD):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successfully(self):
        """Test successfully creating a new user with an email."""
        user = create_sample_user()

        self.assertEqual(user.email, SAFE_EMAIL)
        self.assertTrue(user.check_password(SAFE_PASSWORD))

    def test_new_user_email_normalize(self):
        """Test that the email for a new user is normalized."""
        capitalized_email = 'email@CAPITALIZE.COM'
        user = create_sample_user(email=capitalized_email)

        self.assertEqual(user.email, 'email@capitalize.com')

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises an error."""
        with self.assertRaises(ValueError):
            create_sample_user(None, SAFE_PASSWORD)

    def test_create_new_superuser(self):
        """Test super user is created sucessfully."""
        user = get_user_model().objects.create_superuser(
            SAFE_EMAIL,
            SAFE_PASSWORD
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=create_sample_user(),
            name='vegan'
            )

        self.assertEqual(str(tag), tag.name)
