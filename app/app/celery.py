import os
from celery import Celery
from kombu import Queue, Exchange
from time import sleep

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

celery_app = Celery("app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.conf.task_queues = [
    Queue(
        "spear_tasks",
        Exchange("spear_tasks"),
        routing_key="spear_tasks",
        queue_arguments={"x-max-priority": 10},
    ),
    # Queue("dead_letter_queue", routing_key="dead_letter_queue"),
]


celery_app.conf.task_acks_late = True
celery_app.conf.task_default_priority = 5
celery_app.conf.worker_prefetch_multiplier = 1

celery_app.autodiscover_tasks()

# base_dir = os.getcwd()
# task_folder = os.path.join(base_dir, "dcelery", "celery_tasks")
# if os.path.exists(task_folder) and os.path.isdir(task_folder):
#     task_modules = []
#     for filename in os.listdir(task_folder):
#         if filename.startswith("ex") and filename.endswith(".py"):
#             module_name = f"dcelery.celery_tasks.{filename[:-3]}"
#             module = __import__(module_name, fromlist=["*"])
#             for name in dir(module):
#                 obj = getattr(module, name)
#                 if callable(obj) and name.startswith("my_task"):
#                     task_modules.append(f"{module_name}.{name}")
#     app.autodiscover_tasks(task_modules)
