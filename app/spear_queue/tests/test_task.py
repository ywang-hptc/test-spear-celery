from django.test import TestCase
from spear_queue.tasks import spear_job
from django.test import override_settings


class TestSpearTask(TestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_spear_task(self):
        result = spear_job.apply_async(
            kwargs={"priority": 1, "params": {"protocol": "test"}}
        )
        self.assertEqual(result.get(), "Finish with priority 1, protocol: test")
