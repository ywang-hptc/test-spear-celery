import os

broker_url = os.environ.get("CELERY_BROKER", "amqp://guest:guest@rabbitmq:5672//")
result_backend = os.environ.get("CELERY_BACKEND", "redis://redis:6379/0")
timezone = os.environ.get("TIMEZONE", "Europe/Amsterdam")
celery_enable_utc = False
