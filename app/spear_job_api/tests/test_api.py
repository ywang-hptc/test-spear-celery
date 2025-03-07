from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from spear_job_api.models import SpearJob
from spear_job_api.serializers import SpearJobSerializer

SPEAR_JOB_URL = reverse("spear_job_api:spearjob-list")


def detail_url(celery_id: str):
    """Create and return a recipe detail URL."""
    return reverse("spear_job:spearjob-detail", args=[celery_id])


def create_spear_job(**params):
    """Create and return a spear job."""
    defaults = {
        "priority": 1,
        "celery_job_id": "1234",
        "args": "()",
        "kwargs": "{'testkey': 'testvalue'}",
    } | params
    spear_job = SpearJob.objects.create(**defaults)
    return spear_job


class SpearJobApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        # setup an authenticated user
        self.client = APIClient()

    def test_create_spear_job(self):
        """Test creating a recipe"""
        payload = {
            "priority": 1,
            "celery_job_id": "test12345",
            "args": "(123)",
            "kwargs": "{'testkey': 'testvalue'}",
        }
        res = self.client.post(SPEAR_JOB_URL, payload)  # /api/recipe/recipes/

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        spear_job = SpearJob.objects.get(id=res.data["id"])
        print(res.data)
        for k, v in payload.items():
            self.assertEqual(getattr(spear_job, k), v)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    # TODO: implement below
    # def test_partial_update_recipe(self):
    #     """Test updating a recipe with patch"""
    #     original_link = "https://example.com/recipe.pdf"
    #     recipe = create_recipe(
    #         user=self.user, title="Sample recipe title", link=original_link
    #     )
    #     payload = {"title": "New recipe title"}
    #     url = detail_url(recipe.id)

    #     res = self.client.patch(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     recipe.refresh_from_db()  # refresh the recipe object from the DB
    #     self.assertEqual(recipe.title, payload["title"])
    #     self.assertEqual(recipe.link, original_link)
    #     self.assertEqual(recipe.user, self.user)

    # def test_full_update(self):
    #     """Test full update of recipe."""
    #     recipe = create_recipe(
    #         user=self.user,
    #         title="Sample recipe title",
    #         time_minutes=22,
    #         price=Decimal("5.25"),
    #         description="Sample recipe description",
    #         link="https://example.com/recipe.pdf",
    #     )

    #     payload = {
    #         "title": "New recipe title",
    #         "time_minutes": 25,
    #         "price": Decimal("6.25"),
    #         "description": "New description",
    #         "link": "https://example.com/updated-recipe.pdf",
    #     }

    #     url = detail_url(recipe.id)
    #     res = self.client.put(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     recipe.refresh_from_db()

    #     for k, v in payload.items():
    #         self.assertEqual(getattr(recipe, k), v)
    #     self.assertEqual(recipe.user, self.user)

    # def test_delete_recipe(self):
    #     """Test deleting a recipe"""
    #     recipe = create_recipe(user=self.user)
    #     url = detail_url(recipe.id)
    #     res = self.client.delete(url)

    #     # successful delete should return 204
    #     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
