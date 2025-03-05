from spear_job_api.models import SpearJob
import celery.signals as celery_signals
from celery import shared_task, Task
import time
from typing import Any
import logging

# set basic config for a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@shared_task(queue="spear_tasks")
def spear_job(priority: int, params: dict[str, Any]):
    time.sleep(5)
    logger.info(f"Running a spear job with priority {priority}")
    return f"Finish with priority {priority}"


@celery_signals.before_task_publish.connect(sender="spear_queue.tasks.spear_job")
def handle_task_before_task_publish(
    sender=None, headers: Any = None, body: dict[str, Any] = None, **_kwargs
):
    logger.info(f"Task before task pubish: {headers=} {body=}")
    print(f"Task before task pubish: {headers=} {body=}")


@celery_signals.after_task_publish.connect(
    sender="spear_queue.tasks.spear_job"
)  # note sender is name for before/after task publish
def handle_task_after_task_publish(
    sender=None, headers: Any = None, body: dict[str, Any] = None, **_kwargs
):
    logger.info(f"Task after task pubish: {headers=} {body=}")
    SpearJob.objects.create(
        params=body[1]["params"],
        priority=body[1]["priority"],
        celery_job_id=headers["id"],
    )


@celery_signals.task_prerun.connect(sender=spear_job)
def handle_task_prerun(
    task_id: str, task: Any, args: list[Any], kwargs: dict[str, Any], **_kwargs
):
    logger.info(f"Task before task run: {task_id=}")


@celery_signals.task_postrun.connect(sender=spear_job)
def handle_task_postrun(
    task_id: str,
    task: Any,
    args: list[Any],
    kwargs: dict[str, Any],
    retval: Any,
    state: str,
    **_kwargs,
):
    logger.info(f"Task after task run: {task_id=}, {state=}, {retval=}")


body = (
    [5, {"params": "foo"}],
    {},
    {"callbacks": None, "errbacks": None, "chain": None, "chord": None},
)
