import os

broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
timezone = "Europe/Amsterdam"
celery_enable_utc = False
