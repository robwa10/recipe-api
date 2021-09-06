from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

SAFE_INGREDIENT_NAME = 'Cinnamon'
SAFE_TAG_NAME = 'Breakfast'
SAFE_TIME_MINUTES = 10
SAFE_TITLE = 'Sample Recipe'
SAFE_PRICE = 5.00


def create_detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_ingredient(user, name=SAFE_INGREDIENT_NAME):
    return Ingredient.objects.create(user=user, name=name)


def create_sample_tag(user, name=SAFE_TAG_NAME):
    return Tag.objects.create(user=user, name=name)


def create_sample_recipe(user, **params):
    defaults = {
        'title': SAFE_TITLE,
        'time_minutes': SAFE_TIME_MINUTES,
        'price': SAFE_PRICE
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
                'user@example.com',
                'testpass'
            )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
                'second_user@example.com',
                'testpass'
            )
        create_sample_recipe(user=user2)
        create_sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        url = create_detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {
            'title': 'Cheesecake',
            'time_minutes': 30,
            'price': 5
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = create_sample_tag(user=self.user)
        tag2 = create_sample_tag(user=self.user, name='Vegan')
        payload = {
            'title': 'Lime Cheescake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 5
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = create_sample_ingredient(user=self.user)
        ingredient2 = create_sample_ingredient(user=self.user, name='Prawns')
        payload = {
            'title': 'Prawn Stirfry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 60,
            'price': 5
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
