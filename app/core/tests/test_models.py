from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


SAFE_EMAIL = 'test@email.com'
SAFE_PASSWORD = 'test123'
SAFE_INGREDIENT = 'Cucumber'
SAFE_RECIPE_TITLE = 'Vegan Pancakes'
SAFE_RECIPE_COOK_TIME = 5
SAFE_RECIPE_PRICE = 5.00
SAFE_TAG = 'vegan'


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
            name=SAFE_TAG
            )

        self.assertEqual(str(tag), SAFE_TAG)

    def test_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user=create_sample_user(),
            name=SAFE_INGREDIENT
        )

        self.assertEqual(str(ingredient), SAFE_INGREDIENT)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=create_sample_user(),
            title=SAFE_RECIPE_TITLE,
            time_minutes=SAFE_RECIPE_COOK_TIME,
            price=SAFE_RECIPE_PRICE
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test images are saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)
