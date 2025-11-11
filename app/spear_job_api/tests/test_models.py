from django.test import TestCase
from spear_job_api import models
import pytz
from unittest import mock
import datetime


class TestSpearJobModel(TestCase):
    def test_create_spear_job(self):
        """Test creating a new spear job."""
        mocked = datetime.datetime(2019, 8, 8, 0, 0, 0, tzinfo=pytz.utc)
        test_paitent_id = "12341234"
        test_priority = 2
        test_celery_job_id = "11223344"
        test_workflow_name = "test_workflow"
        test_workflow_config = {"key1": "test1", "key2": 2}
        test_raystation_system = models.RayStationSystem.objects.create(
            system_name="TestSystem", system_uid="UID1234"
        )
        with mock.patch("django.utils.timezone.now", mock.Mock(return_value=mocked)):
            spear_job = models.SpearJob.objects.create(
                priority=test_priority,
                celery_job_id=test_celery_job_id,
                workflow_config=test_workflow_config,
                workflow_name=test_workflow_name,
                raystation_system=test_raystation_system,
            )

            self.assertEqual(spear_job.priority, 1)
            self.assertEqual(spear_job.celery_job_id, "11223344")
            self.assertEqual(spear_job.status, "PENDING")
            # Mocked datetime is used to compare the created_at field
            self.assertEqual(spear_job.created_at, mocked)
            self.assertEqual(spear_job.workflow_name, "test_workflow")
            self.assertEqual(spear_job.workflow_config, test_workflow_config)
            self.assertEqual(spear_job.raystation_system.system_name, "TestSystem")
            self.assertEqual(spear_job.raystation_system.system_uid, "UID1234")

    # def test_auto_update_worker_name(self):
    #     """Test auto updating worker name."""
    #     spear_job = models.SpearJob.objects.create(
    #         priority=1,
    #         celery_job_id="1234",
    #         args="()",
    #         kwargs="{'testkey': 'testvalue'}",
    #     )
    #     self.assertEqual(spear_job.server_name, "")
    #     spear_job.worker_name = "servera"
    #     spear_job.save()
    #     self.assertEqual(spear_job.server_name, models.SpearServerName.SPEAR_SERVER_A)

    #     spear_job.worker_name = "serverb"
    #     spear_job.save()
    #     self.assertEqual(spear_job.server_name, models.SpearServerName.SPEAR_SERVER_B)
