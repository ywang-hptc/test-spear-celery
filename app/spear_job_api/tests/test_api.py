from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from spear_job_api import models
from spear_job_api.serializers import SpearJobSerializer
from django.utils import timezone
import pytz
import datetime

# SPEAR_JOB_URL = reverse("spear_job_api:spearjob-list")
SPEAR_JOB_CREATE_URL = reverse("spear_job_api:spearjob-list")
# /api/spear_job/create/


def detail_url(celery_id: str):
    """Create and return a recipe detail URL."""
    return reverse("spear_job_api:spearjob-detail", args=[celery_id])


def create_spear_job(**params) -> models.SpearJob:
    """Create and return a spear job."""
    defaults = {
        "patient_id": "test_pid",
        "priority": 1,
        "celery_job_id": "test_celery_id",
        "workflow_config": {},
        "workflow_name": "test_workflow",
        "raystation_system": models.RayStationSystem.objects.get_or_create(
            system_name="TestSystem2", system_uid="UID5678"
        ),
    } | params

    spear_job = models.SpearJob.objects.create(**defaults)
    return spear_job


def create_user(email="user2example.com", password="testpass123"):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(email, password)  # type: ignore


class SpearJobApiTests(APITestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.system = models.RayStationSystem.objects.create(
            system_name="TestRayStationSystem", system_uid="UID9999"
        )

    def test_create_spear_job(self):
        """Test creating a spear job"""
        payload = {
            "patient_id": "patient_001",
            "priority": 1,
            "celery_job_id": "test12345",
            "workflow_name": "test_workflow_1",
            "workflow_config": {"plan": "A", "beam_set": 2},
            "raystation_system": "TestRayStationSystem",
        }
        res = self.client.post(SPEAR_JOB_CREATE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        spear_job = models.SpearJob.objects.get(celery_job_id=res.data["celery_job_id"])
        self.assertEqual(spear_job.patient_id, payload["patient_id"])
        self.assertEqual(spear_job.priority, payload["priority"])
        self.assertEqual(spear_job.workflow_name, payload["workflow_name"])
        self.assertEqual(spear_job.workflow_config, payload["workflow_config"])
        self.assertEqual(spear_job.raystation_system, self.system)

    # def test_get_spear_job_detail(self):
    #     """Test get the detail of the spear job"""
    #     spear_job = create_spear_job(celery_job_id="test1234")
    #     url = detail_url(celery_id="test1234")
    #     res = self.client.get(url)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     serializer = SpearJobSerializer(spear_job)
    #     self.assertEqual(res.data, serializer.data)

    # def test_partial_update_spear_job_prerun(self):
    #     """Test updating a spear job data with patch, changing status to RUNNING"""
    #     spear_job = create_spear_job(celery_job_id="test4321")
    #     url = detail_url(celery_id="test4321")
    #     payload = {
    #         "status": "RUNNING",
    #         "started_at": datetime.datetime(
    #             2023, 11, 10, 0, 0, 0, tzinfo=pytz.utc
    #         ).isoformat(),
    #         "worker_name": "workerA",
    #     }
    #     res = self.client.patch(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     spear_job.refresh_from_db()  # refresh the recipe object from the DB
    #     self.assertEqual(spear_job.status, "RUNNING")
    #     self.assertEqual(
    #         spear_job.started_at,
    #         datetime.datetime(2023, 11, 10, 0, 0, 0),
    #     )
    #     self.assertEqual(spear_job.worker_name, "workerA")

    # def test_partial_update_spear_job_postrun_success(self):
    #     """Test updating a spear job data with patch, changing status to SUCCESS"""
    #     spear_job = create_spear_job(celery_job_id="test43210")
    #     url = detail_url(celery_id="test43210")
    #     payload = {
    #         "status": "SUCCESS",
    #         "completed_at": datetime.datetime(
    #             2023, 11, 10, 0, 0, 0, tzinfo=pytz.utc
    #         ).isoformat(),
    #         "result": "test_job_result",
    #     }
    #     res = self.client.patch(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     spear_job.refresh_from_db()  # refresh the recipe object from the DB
    #     self.assertEqual(spear_job.status, "SUCCESS")
    #     self.assertEqual(
    #         spear_job.completed_at,
    #         datetime.datetime(2023, 11, 10, 0, 0, 0),
    #     )
    #     self.assertEqual(spear_job.result, "test_job_result")
    #     self.assertIsNone(spear_job.error)

    # def test_partial_update_spear_job_postrun(self):
    #     """Test updating a spear job data with patch, changing status to FAILURE"""
    #     spear_job = create_spear_job(celery_job_id="test543210")
    #     url = detail_url(celery_id="test543210")
    #     payload = {
    #         "status": "FAILURE",
    #         "completed_at": datetime.datetime(
    #             2023, 11, 10, 0, 0, 0, tzinfo=pytz.utc
    #         ).isoformat(),
    #         "error": "test_job_error_message",
    #     }
    #     res = self.client.patch(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     spear_job.refresh_from_db()  # refresh the recipe object from the DB
    #     self.assertEqual(spear_job.status, "FAILURE")
    #     self.assertEqual(
    #         spear_job.completed_at,
    #         datetime.datetime(2023, 11, 10, 0, 0, 0),
    #     )
    #     self.assertIsNone(spear_job.result)
    #     self.assertEqual(spear_job.error, "test_job_error_message")
