from django.core.management.base import BaseCommand
from spear_queue.tasks import spear_job


class Command(BaseCommand):
    help = "Create a task for DEMO"

    def add_arguments(self, parser):
        parser.add_argument("priority", type=int, help="Priority of the task")

    def handle(self, *args, **kwargs):
        priority = kwargs["priority"]
        # Get the priority from the command arguments
        self.stdout.write(
            self.style.SUCCESS(f"Starting task with priority {priority}...")
        )
        spear_job.apply_async(
            kwargs={"priority": priority, "params": {"params": "foo"}},
            priority=priority,
        )

        self.stdout.write(self.style.SUCCESS("Task added to queue"))
