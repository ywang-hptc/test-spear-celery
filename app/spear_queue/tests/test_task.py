from django.test import TestCase
from spear_queue.tasks import enqueue_spear_job
from django.test import override_settings
from spear_job_api.models import SpearJob, RayStationSystem


def create_raystation_system(name="Test RayStation System"):
    return RayStationSystem.objects.create(system_name=name, system_uid="UID_TEST")


class TestSpearTask(TestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_spear_task(self):
        raystation_system = create_raystation_system()
        payload = {
            "patient_id": "test_patient",
            "priority": 1,
            "raystation_system": raystation_system.system_name,
            "workflow_name": "Test Workflow",
            "workflow_config": {"protocol": "test"},
        }
        result = enqueue_spear_job.apply_async(payload=payload)
        self.assertTrue(result.successful())
        spear_job = SpearJob.objects.get(celery_job_id=result.id)
        self.assertEqual(spear_job.patient_id, "test_patient")
        self.assertEqual(spear_job.workflow_name, "Test Workflow")
        self.assertEqual(spear_job.workflow_config, {"protocol": "test"})
