from django.core.management.base import BaseCommand
from spear_queue.tasks import enqueue_spear_job


class Command(BaseCommand):
    help = "Create a task for DEMO"

    def add_arguments(self, parser):
        parser.add_argument("priority", type=int, help="Priority of the task")
        parser.add_argument("workflow_name", type=str, help="Workflow name")

    def handle(self, *args, **kwargs):
        priority = kwargs["priority"]
        workflow_name = kwargs["workflow_name"]
        # Get the priority from the command arguments
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting task with priority {priority}, workflow_name: {workflow_name}"
            )
        )
        payload = {
            "patient_id": "12345678",
            "priority": priority,
            "raystation_system": "Spear Development",
            "workflow_name": workflow_name,
            "workflow_config": {"key1": "value1", "key2": 2},
        }
        enqueue_spear_job.apply_async(
            kwargs={
                "payload": payload,
            },
        )

        self.stdout.write(self.style.SUCCESS("Task added to queue"))
