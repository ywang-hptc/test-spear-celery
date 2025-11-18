from time import timezone
from django.test import TestCase
from spear_queue.tasks import enqueue_spear_job, handle_task_after_task_publish
from django.test import override_settings
from spear_job_api.models import SpearJob, RayStationSystem


def create_raystation_system(name="Test RayStation System"):
    return RayStationSystem.objects.create(system_name=name, system_uid="UID_TEST")


class TestSpearTask(TestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    def test_handle_task_after_task_publish(self):
        create_raystation_system("Test Ray System")
        celery_id = "7a4b5a64-ec4e-4a0f-a3e6-1c8dc3c977fb"
        headers = {
            "lang": "py",
            "task": "spear_queue.tasks.enqueue_spear_job",
            "id": celery_id,
            "shadow": None,
            "eta": None,
            "expires": None,
            "group": None,
            "group_index": None,
            "retries": 0,
            "timelimit": [None, None],
            "root_id": celery_id,
            "parent_id": None,
            "argsrepr": "()",
            "kwargsrepr": "{'payload': {'patient_id': 'test_pt1', 'priority': 2, 'raystation_system': 'Test Ray System', 'workflow_name': 'test_workflow_1', 'workflow_config': {'key1': 'value1', 'key2': 2}}}",
            "origin": "gen1@e3195a40bfb1",
            "ignore_result": False,
            "replaced_task_nesting": 0,
            "stamped_headers": None,
            "stamps": {},
        }
        body = (
            (),
            {
                "payload": {
                    "patient_id": "test_pt1",
                    "priority": 2,
                    "raystation_system": "Test Ray System",
                    "workflow_name": "test_workflow_1",
                    "workflow_config": {"key1": "value1", "key2": 2},
                }
            },
            {"callbacks": None, "errbacks": None, "chain": None, "chord": None},
        )

        handle_task_after_task_publish(
            sender="spear_queue.tasks.enqueue_spear_job",
            headers=headers,
            body=body,
        )
        job = SpearJob.objects.get(celery_job_id=celery_id)
        self.assertEqual(job.status, "QUEUED")
        self.assertEqual(job.patient_id, "test_pt1")
        self.assertEqual(job.priority, 2)
        self.assertEqual(job.workflow_name, "test_workflow_1")
        self.assertEqual(job.workflow_config, {"key1": "value1", "key2": 2})
        self.assertEqual(job.raystation_system.system_name, "Test Ray System")
