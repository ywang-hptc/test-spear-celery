from django.test import TestCase
from unittest.mock import patch, MagicMock
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

    def test_revoke_spear_job_by_from_spear_id_success(self):
        """Test successful revocation of a spear job via service layer."""
        spear_job = models.SpearJob.objects.create(
            patient_id="11223344",
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb",
            workflow_name="initial_workflow",
            workflow_config={"param1": "value1"},
            raystation_system=self.raystation_system,
            priority=3,
            status="RUNNING",
        )
        self.assertEqual(spear_job.status, "RUNNING")
        revoked_job = services.revoke_spear_job(spear_job_id=spear_job.id)
        self.assertEqual(revoked_job.status, "REVOKED")

    def test_revoke_spear_job_by_from_celery_id_success(self):
        """Test successful revocation of a spear job via service layer using celery_job_id."""
        spear_job = models.SpearJob.objects.create(
            patient_id="11223344",
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb",
            workflow_name="initial_workflow",
            workflow_config={"param1": "value1"},
            raystation_system=self.raystation_system,
            priority=3,
            status="RUNNING",
        )
        self.assertEqual(spear_job.status, "RUNNING")
        revoked_job = services.revoke_spear_job(
            celery_job_id="7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb"
        )
        self.assertEqual(revoked_job.status, "REVOKED")

    def test_revoke_spear_job_no_identifier_error(self):
        """Test that revoking a spear job without an identifier raises ValueError."""
        with self.assertRaises(ValueError) as context:
            services.revoke_spear_job(spear_job_id=None, celery_job_id=None)

        self.assertEqual(
            str(context.exception), "Provide either spear_job_id or celery_job_id."
        )


class TestSpearWorkflowConfigLoading(TestCase):
    @patch("spear_job_api.services.resources.files")
    def test_list_workflow_files(self, mock_files):
        # Create fake Path objects
        fake_path_1 = MagicMock()
        fake_path_1.stem = "test_workflow_1"
        fake_path_1.suffix = ".json"

        fake_path_2 = MagicMock()
        fake_path_2.stem = "test_workflow_2"
        fake_path_2.suffix = ".json"

        fake_non_json = MagicMock()
        fake_non_json.stem = "non_workflow_file"
        fake_non_json.suffix = ".txt"

        # Mock pkg.iterdir()
        fake_pkg = MagicMock()
        fake_pkg.iterdir.return_value = [fake_path_2, fake_non_json, fake_path_1]

        mock_files.return_value = fake_pkg

        result = services.list_workflow_files()

        self.assertEqual(result, ["test_workflow_1", "test_workflow_2"])

    def test_load_spear_workflow_config_no_filename(self):
        """Test loading workflow config with no filename raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError) as context:
            services.load_spear_workflow_config(filename=None)

    def test_load_spear_workflow_config_file_not_found(self):
        """Test loading workflow config with non-existent filename raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError) as context:
            services.load_spear_workflow_config(filename="non_existent_workflow")

    @patch("spear_job_api.services.resources.read_text")
    def test_load_spear_workflow_config_success(self, mock_read_text):
        """Test successful loading of a workflow config."""
        mock_read_text.return_value = (
            '{"workflow_key1": "workflow_value1", "workflow_key2": 2}'
        )

        config = services.load_spear_workflow_config("workflow_b")

        mock_read_text.assert_called_once_with(
            "spear_job_api.spear_workflows",
            "workflow_b.json",
            encoding="utf-8",
        )

        self.assertEqual(
            config, {"workflow_key1": "workflow_value1", "workflow_key2": 2}
        )
