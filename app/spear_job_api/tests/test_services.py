from django.test import TestCase
from spear_job_api import models
from spear_job_api import services
from rest_framework import serializers
import pytz
from unittest import mock
import datetime


class TestSpearJobServices(TestCase):
    def setUp(self):
        self.raystation_system = models.RayStationSystem.objects.create(
            system_name="TestSystem", system_uid="UID1234"
        )

    def test_create_spear_job_success(self):
        """Test successful creation of a spear job via service layer."""
        mocked_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=pytz.utc)
        data = {
            "patient_id": "11223344",
            "celery_job_id": "7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb",
            "workflow_name": "service_workflow",
            "workflow_config": {"param1": "value1"},
            "raystation_system": self.raystation_system.system_name,
            "priority": 3,
        }
        with mock.patch(
            "django.utils.timezone.now", mock.Mock(return_value=mocked_time)
        ):

            spear_job = services.create_spear_job(data=data)
            self.assertEqual(spear_job.patient_id, "11223344")
            # celery job id in serialized os uuid format, we compare as string
            self.assertEqual(
                str(spear_job.celery_job_id), "7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb"
            )
            self.assertEqual(spear_job.workflow_name, "service_workflow")
            self.assertEqual(spear_job.workflow_config, {"param1": "value1"})
            self.assertEqual(spear_job.raystation_system.system_name, "TestSystem")
            self.assertEqual(spear_job.priority, 3)
            self.assertEqual(spear_job.created_at, mocked_time)
            self.assertEqual(spear_job.status, "PENDING")

    def test_create_spear_job_validation_error(self):
        """Test creation of a spear job with invalid data raises ValidationError."""
        data = {
            "patient_id": "",
            "celery_job_id": "invalid-uuid",
            "workflow_name": "service_workflow",
            "workflow_config": {"param1": "value1"},
            "raystation_system": "NonExistentSystem",
            "priority": -1,
        }

        with self.assertRaises(serializers.ValidationError) as context:
            services.create_spear_job(data=data)

        errors = context.exception.detail
        self.assertIn("patient_id", errors)
        self.assertIn("celery_job_id", errors)
        self.assertIn("raystation_system", errors)
        self.assertIn("priority", errors)

    def test_update_spear_job_from_spear_id_success(self):
        """Test successful update of a spear job via service layer."""
        spear_job = models.SpearJob.objects.create(
            patient_id="11223344",
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb",
            workflow_name="initial_workflow",
            workflow_config={"param1": "value1"},
            raystation_system=self.raystation_system,
            priority=3,
            status="PENDING",
        )

        update_data = {
            "status": "RUNNING",
            "append_log": "Job started.",
            "worker_name": "Worker1",
            "started_at": datetime.datetime.now(pytz.utc),
        }

        updated_job = services.update_spear_job(
            spear_job_id=spear_job.id, data=update_data
        )

        self.assertEqual(updated_job.status, "RUNNING")
        self.assertEqual(updated_job.logs, "Job started.")
        self.assertEqual(updated_job.worker_name, "Worker1")

    def test_update_spear_job_from_celery_id_success(self):
        """Test successful update of a spear job via service layer using celery_job_id."""
        spear_job = models.SpearJob.objects.create(
            patient_id="11223344",
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb",
            workflow_name="initial_workflow",
            workflow_config={"param1": "value1"},
            raystation_system=self.raystation_system,
            priority=3,
            status="PENDING",
        )

        update_data = {
            "status": "COMPLETED",
            "append_logs": ["Job started.", "Job completed successfully."],
            "worker_name": "Worker1",
            "completed_at": datetime.datetime.now(pytz.utc),
        }

        updated_job = services.update_spear_job(
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb", data=update_data
        )

        self.assertEqual(updated_job.status, "COMPLETED")
        self.assertEqual(updated_job.logs, "Job started.\nJob completed successfully.")
        self.assertEqual(updated_job.worker_name, "Worker1")

    def test_update_spear_job_no_identifier_error(self):
        """Test that updating a spear job without an identifier raises ValueError."""
        update_data = {
            "status": "RUNNING",
            "append_log": "Job started.",
            "worker_name": "Worker1",
        }

        with self.assertRaises(ValueError) as context:
            services.update_spear_job(data=update_data)

        self.assertEqual(
            str(context.exception), "Provide either spear_job_id or celery_job_id."
        )

    def test_update_spear_job_validation_error(self):
        """Test that updating a spear job with invalid data raises ValidationError."""
        spear_job = models.SpearJob.objects.create(
            patient_id="11223344",
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb",
            workflow_name="initial_workflow",
            workflow_config={"param1": "value1"},
            raystation_system=self.raystation_system,
            priority=3,
            status="PENDING",
        )

        update_data = {
            "status": "INVALID_STATUS",
            "append_log": "Job started.",
            "worker_name": "Worker1",
        }

        with self.assertRaises(serializers.ValidationError) as context:
            services.update_spear_job(spear_job_id=spear_job.id, data=update_data)

        errors = context.exception.detail
        self.assertIn("status", errors)
