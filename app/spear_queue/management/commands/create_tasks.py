from django.core.management.base import BaseCommand
from spear_queue.tasks import spear_job


class Command(BaseCommand):
    help = "Create a task for DEMO"

    def handle(self, *args, **kwargs):
        # Get the priority from the command arguments
        for priority in range(1, 11):
            # Start the Celery task with the given priority
            self.stdout.write(
                self.style.SUCCESS(f"Starting task with priority {priority}...")
            )
            spear_job.apply_async(args=[priority], priority=priority)

            self.stdout.write(self.style.SUCCESS("Task added to queue"))
