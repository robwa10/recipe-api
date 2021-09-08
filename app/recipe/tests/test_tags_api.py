from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')
SAFE_EMAIL = 'test@email.com'
SAFE_PASSWORD = 'test123'

SAFE_TAG_NAME = 'Breakfast'
SAFE_TIME_MINUTES = 10
SAFE_TITLE = 'Sample Recipe'
SAFE_PRICE = 5.00


def create_sample_user(email=SAFE_EMAIL, password=SAFE_PASSWORD):
    return get_user_model().objects.create_user(email, password)


def create_sample_recipe(user, **params):
    defaults = {
        'title': SAFE_TITLE,
        'time_minutes': SAFE_TIME_MINUTES,
        'price': SAFE_PRICE
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_sample_tag(user, name=SAFE_TAG_NAME):
    return Tag.objects.create(user=user, name=name)


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    def setUp(self):
        self.user = create_sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags returned are for authenticated user"""
        user2 = create_sample_user(email='user2@email.com', password='pass123')
        Tag.objects.create(user=user2, name='Vegitarian')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        payload = {'name': 'Test Tag'}
        self.client.post(TAGS_URL, payload)

        tag_exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(tag_exists)

    def test_create_tag_invalid(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        tag1 = create_sample_tag(user=self.user)
        tag2 = create_sample_tag(user=self.user, name='Lunch')
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        tag = create_sample_tag(user=self.user)
        create_sample_tag(user=self.user, name='Lunch')

        recipe1 = create_sample_recipe(user=self.user)
        recipe2 = create_sample_recipe(user=self.user, title='Lunch Recipe')

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
