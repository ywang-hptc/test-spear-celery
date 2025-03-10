from celery import Celery
from kombu import Queue, Exchange

app = Celery("app")
app.config_from_object("celeryconfig")
app.conf.imports = ("spear_queue.tasks",)
app.conf.task_queues = [
    Queue(
        "spear_tasks",
        Exchange("spear_tasks"),
        routing_key="spear_tasks",
        queue_arguments={"x-max-priority": 10},
    ),
    # Queue("dead_letter_queue", routing_key="dead_letter_queue"),
]
app.conf.task_acks_late = True
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.autodiscover_tasks()
