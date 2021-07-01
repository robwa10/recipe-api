from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')
SAFE_EMAIL = 'test@email.com'
SAFE_PASSWORD = 'test123'
SAFE_INGREDIENT_ONE = 'Cucumber'
SAFE_INGREDIENT_TWO = 'Bacon'


def create_sample_user(email=SAFE_EMAIL, password=SAFE_PASSWORD):
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    def setUp(self):
        self.user = create_sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name=SAFE_INGREDIENT_ONE)
        Ingredient.objects.create(user=self.user, name=SAFE_INGREDIENT_TWO)

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients returned are for authenticated user"""
        user2 = create_sample_user(email='user2@email.com', password='pass123')
        Ingredient.objects.create(user=user2, name=SAFE_INGREDIENT_ONE)
        ingredient = Ingredient.objects.create(
            user=self.user,
            name=SAFE_INGREDIENT_TWO
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        payload = {'name': SAFE_INGREDIENT_ONE}
        self.client.post(INGREDIENTS_URL, payload)

        ingredient_exists = Ingredient.objects.filter(
            user=self.user,
            name=SAFE_INGREDIENT_ONE
        ).exists()
        self.assertTrue(ingredient_exists)

    def test_create_ingredient_invalid(self):
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
