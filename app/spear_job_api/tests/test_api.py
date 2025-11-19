from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from spear_job_api import models
from spear_job_api.serializers import SpearJobCreateSerializer, SpearJobDetailSerializer
from django.utils import timezone
import pytz
import datetime

SPEAR_JOB_URL = reverse("spear_job_api:spearjob-list")
# /api/spear-jobs/
SPEAR_WORKFLOW_URL = reverse("spear_job_api:spearworkflow-list")


def spear_job_detail_url(spear_job_id: str):
    """Create and return a spear job detail URL."""
    # /api/spear-jobs/{spear_job_id}/
    return reverse("spear_job_api:spearjob-detail", args=[spear_job_id])


def celery_job_id_url(celery_job_id: str):
    """Create and return a spear job detail URL by celery job id."""
    # /api/spear-jobs/by-celery/{celery_job_id}/
    return reverse("spear_job_api:spearjob-by-celery-job-id", args=[celery_job_id])


def spear_workflow_detail_url(workflow_name: str):
    """Create and return a spear workflow detail URL."""
    # /api/spear-workflows/{workflow_name}/
    return reverse("spear_job_api:spearworkflow-detail", args=[workflow_name])


def create_spear_job(**params) -> models.SpearJob:
    """Create and return a spear job."""
    defaults = {
        "patient_id": "test_pid",
        "priority": 1,
        "celery_job_id": "52a92938-8fc1-4b04-8ab0-0d2a6111e76b",
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
        self.raystation_system = models.RayStationSystem.objects.create(
            system_name="TestRayStationSystem", system_uid="UID9999"
        )

    def test_create_spear_job(self):
        """Test creating a spear job"""
        payload = {
            "patient_id": "patient_001",
            "priority": 1,
            "celery_job_id": "9363d9ab-c29d-4ec8-af36-68445cee6f97",
            "workflow_name": "test_workflow_1",
            "workflow_config": {"plan": "A", "beam_number": 2},
            "raystation_system": "TestRayStationSystem",
            "status": "QUEUED",
        }
        res = self.client.post(SPEAR_JOB_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        spear_job = models.SpearJob.objects.get(celery_job_id=res.data["celery_job_id"])

        self.assertEqual(spear_job.patient_id, payload["patient_id"])
        self.assertEqual(spear_job.priority, payload["priority"])
        self.assertEqual(spear_job.workflow_name, payload["workflow_name"])
        self.assertEqual(spear_job.workflow_config, payload["workflow_config"])
        self.assertEqual(spear_job.raystation_system, self.raystation_system)

    def test_get_spear_job_detail(self):
        """Test get the detail of the spear job by job id in the url"""
        spear_job = create_spear_job(
            patient_id="patient_002",
            priority=3,
            celery_job_id="e026506c-0070-4e0e-80e2-b365e635d7d8",
            workflow_name="test_workflow_2",
            workflow_config={"plan": "B", "beam_number": 123},
            raystation_system=self.raystation_system,
        )
        spear_job_id = spear_job.id
        url = spear_job_detail_url(spear_job_id=spear_job_id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = SpearJobDetailSerializer(spear_job)
        self.assertEqual(res.data["raystation_system_name"], "TestRayStationSystem")
        self.assertEqual(res.data["raystation_system_uid"], "UID9999")
        self.assertEqual(res.data, serializer.data)

    def test_get_spear_job_by_celery_job_id_success(self):
        """Test get the detail of the spear job by celery job id in the url"""
        spear_job = create_spear_job(
            patient_id="patient_003",
            priority=2,
            celery_job_id="de20ad94-54d8-48b4-a08a-b8a5590e9edb",
            workflow_name="test_workflow_3",
            workflow_config={"plan": "C", "beam_number": 456},
            raystation_system=self.raystation_system,
        )
        celery_job_id = spear_job.celery_job_id
        url = celery_job_id_url(celery_job_id=str(celery_job_id))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = SpearJobDetailSerializer(spear_job)
        self.assertEqual(
            res.data["celery_job_id"], "de20ad94-54d8-48b4-a08a-b8a5590e9edb"
        )
        self.assertEqual(res.data, serializer.data)

    def test_get_spear_job_by_celery_job_id_not_found(self):
        """Test get the detail of the spear job by celery job id that does not exist"""
        url = celery_job_id_url(celery_job_id="3b7cd972-f5cf-4f12-9705-6b78de3236b4")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_spear_job_prerun(self):
        """Test updating a spear job data with patch, changing status to RUNNING"""
        spear_job = create_spear_job(
            patient_id="patient_004",
            priority=6,
            celery_job_id="02cf3bc7-6aae-4b01-8310-28aa82dda6a2",
            workflow_name="test_workflow_4",
            workflow_config={"plan": "D", "beam_number": 888},
            raystation_system=self.raystation_system,
        )
        url = spear_job_detail_url(spear_job_id=spear_job.id)
        payload = {
            "status": "RUNNING",
            "started_at": datetime.datetime(
                2023, 11, 10, 0, 0, 0, tzinfo=pytz.utc
            ).isoformat(),
            "worker_name": "worker_sp1",
            "append_log": "Job started.",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        spear_job.refresh_from_db()
        self.assertEqual(spear_job.status, "RUNNING")
        self.assertEqual(
            spear_job.started_at,
            datetime.datetime(2023, 11, 10, 0, 0, 0, tzinfo=pytz.utc),
        )
        self.assertEqual(spear_job.worker_name, "worker_sp1")
        self.assertEqual(spear_job.server_name, "HPTC-RAY-SP01")
        self.assertEqual(spear_job.logs, "Job started.")

    def test_partial_update_spear_job_postrun_success(self):
        """Test updating a spear job data with patch, changing status to COMPLETED"""
        spear_job = create_spear_job(
            patient_id="patient_005",
            priority=8,
            celery_job_id="57ff3ae9-9cbe-4c77-1910-28bb22a3a1b3",
            workflow_name="test_workflow_5",
            workflow_config={"plan": "EE", "beam_number": 1},
            raystation_system=self.raystation_system,
        )
        url = spear_job_detail_url(spear_job_id=spear_job.id)
        payload = {
            "status": "COMPLETED",
            "completed_at": datetime.datetime(
                2023, 11, 11, 0, 0, 0, tzinfo=pytz.utc
            ).isoformat(),
            "append_log": "job completed successfully.",
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        spear_job.refresh_from_db()
        self.assertEqual(spear_job.status, "COMPLETED")
        self.assertEqual(
            spear_job.completed_at,
            datetime.datetime(2023, 11, 11, 0, 0, 0, tzinfo=pytz.utc),
        )
        self.assertEqual(spear_job.logs, "job completed successfully.")

    def test_partial_update_spear_job_postrun(self):
        """Test updating a spear job data with patch, changing status to FAILURE"""
        spear_job = create_spear_job(
            patient_id="patient_006",
            priority=2,
            celery_job_id="a3ff3ae9-9cbe-4c77-1910-28bb22a3a1b4",
            workflow_name="test_workflow_6",
            workflow_config={"plan": "DD", "beam_number": 2},
            raystation_system=self.raystation_system,
        )
        url = spear_job_detail_url(spear_job_id=spear_job.id)
        payload = {
            "status": "FAILED",
            "completed_at": datetime.datetime(
                2023, 12, 13, 0, 0, 0, tzinfo=pytz.utc
            ).isoformat(),
            "append_logs": ["log", "job failed."],
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        spear_job.refresh_from_db()
        self.assertEqual(spear_job.status, "FAILED")
        self.assertEqual(
            spear_job.completed_at,
            datetime.datetime(2023, 12, 13, 0, 0, 0, tzinfo=pytz.utc),
        )
        self.assertEqual(spear_job.logs, "log\njob failed.")

    def test_partial_update_spear_job_append_logs(self):
        """Test updating a spear job data with patch,with append_logs or append_log"""
        spear_job = create_spear_job(
            patient_id="patient_007",
            priority=4,
            celery_job_id="b4ff3ae9-9cbe-4c77-1910-28bb22a3a1b5",
            workflow_name="test_workflow_7",
            workflow_config={"plan": "FF", "beam_number": 3},
            raystation_system=self.raystation_system,
        )
        url = spear_job_detail_url(spear_job_id=spear_job.id)
        payload1 = {
            "append_log": "First log entry.",
        }
        res1 = self.client.patch(url, payload1)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        spear_job.refresh_from_db()
        self.assertEqual(spear_job.logs, "First log entry.")

        payload2 = {
            "append_logs": ["Second log entry.", "Third log entry."],
        }
        res2 = self.client.patch(url, payload2)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        spear_job.refresh_from_db()
        self.assertEqual(
            spear_job.logs, "First log entry.\nSecond log entry.\nThird log entry."
        )

        payload3 = {
            "append_log": "Fourth log entry.",
        }
        res3 = self.client.patch(url, payload3)
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        spear_job.refresh_from_db()
        self.assertEqual(
            spear_job.logs,
            "First log entry.\nSecond log entry.\nThird log entry.\nFourth log entry.",
        )

    def test_list_jobs(self):
        # create a couple of jobs in the DB...
        spear_job1 = create_spear_job(
            patient_id="patient_010",
            priority=3,
            celery_job_id="a4ff3ae9-9cbe-4c77-1910-28bb22a3a1b6",
            workflow_name="test_workflow_7",
            workflow_config={"plan": "FF", "beam_number": 3},
            raystation_system=self.raystation_system,
        )
        spear_job2 = create_spear_job(
            patient_id="patient_011",
            priority=4,
            celery_job_id="e",
            workflow_name="test_workflow_7",
            workflow_config={"plan": "FF", "beam_number": 3},
            raystation_system=self.raystation_system,
        )
        url = reverse("spear_job_api:spearjob-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertEqual(len(resp.data), 2)


class SpearWorkflowApiTests(APITestCase):
    """Test Spear Workflow API requests"""

    @patch("spear_job_api.services.resources.files")
    def test_list_spear_workflows_success(self, mock_files):
        """Test listing available spear workflows"""
        mock_path1 = MagicMock()
        mock_path1.suffix = ".json"
        mock_path1.stem = "workflow_1"
        mock_path2 = MagicMock()
        mock_path2.suffix = ".json"
        mock_path2.stem = "workflow_2"
        mock_path3 = MagicMock()
        mock_path3.suffix = ".txt"  # should be ignored
        mock_path3.stem = "not_a_workflow"

        mock_files.return_value.iterdir.return_value = [
            mock_path1,
            mock_path2,
            mock_path3,
        ]

        url = reverse("spear_job_api:spearworkflow-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(["workflow_1", "workflow_2"], res.data)

    @patch("spear_job_api.services.resources.read_text")
    def test_retrieve_spear_workflow_success(self, mock_read_text):
        """Test retrieving a spear workflow configuration successfully"""
        mock_read_text.return_value = (
            '{"workflow_key1": "workflow_value1", "workflow_key2": 2}'
        )

        workflow_name = "workflow_a"
        url = spear_workflow_detail_url(workflow_name=workflow_name)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data, {"workflow_key1": "workflow_value1", "workflow_key2": 2}
        )
        mock_read_text.assert_called_once_with(
            "spear_job_api.spear_workflows",
            f"{workflow_name}.json",
            encoding="utf-8",
        )

    def test_retrieve_spear_workflow_not_found(self):
        """Test retrieving a non-existent spear workflow returns 404"""
        workflow_name = "non_existent_workflow"
        url = spear_workflow_detail_url(workflow_name=workflow_name)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def tset_retrieve_spear_workflow_no_name(self):
        """Test retrieving a spear workflow with no name returns 404"""
        workflow_name = ""
        url = spear_workflow_detail_url(workflow_name=workflow_name)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
