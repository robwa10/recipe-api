from django.test import TestCase
from django.contrib.auth import get_user_model

test_email = 'test@email.com'
password = 'test123'


class ModelTests(TestCase):
    def test_create_user_with_email_successfully(self):
        """Test successfully creating a new user with an email."""
        user = get_user_model().objects.create_user(
            email=test_email,
            password=password
            )

        self.assertEqual(user.email, test_email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test that the email for a new user is normalized."""
        capitalized_email = 'email@CAPITALIZE.COM'
        user = get_user_model().objects.create_user(
            capitalized_email,
            password
            )

        self.assertEqual(user.email, 'email@capitalize.com')

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises an error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, password)

    def test_create_new_superuser(self):
        """Test super user is created sucessfully."""
        user = get_user_model().objects.create_superuser(
            test_email,
            password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
