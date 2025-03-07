from django.core.management.base import BaseCommand
from spear_queue.tasks import spear_job


class Command(BaseCommand):
    help = "Create a task for DEMO"

    def add_arguments(self, parser):
        parser.add_argument("priority", type=int, help="Priority of the task")
        parser.add_argument("protocol", type=str, help="Protocol name")

    def handle(self, *args, **kwargs):
        priority = kwargs["priority"]
        protocol = kwargs["protocol"]
        # Get the priority from the command arguments
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting task with priority {priority}, protocol: {protocol}"
            )
        )
        spear_job.apply_async(
            kwargs={"priority": priority, "params": {"protocol": protocol}},
            priority=priority,
        )

        self.stdout.write(self.style.SUCCESS("Task added to queue"))
