from celery import shared_task
import time

import logging

# set basic config for a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@shared_task(queue="spear_tasks")
def spear_job(p: int):
    time.sleep(5)
    logger.info(f"Running a spear job with priority {p}")
    return f"Finish with priority {p}"
