import os
import time
from django.utils import timezone
import celery.signals as celery_signals
from celery import shared_task, Task
from typing import Any
import logging
from spear_job_api.models import SpearJob
import requests

# set basic config for a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@shared_task(queue="spear_tasks")
def spear_job(priority: int, params: dict[str, Any]) -> str:
    time.sleep(5)
    logger.info(f"Running a spear job with priority {priority}")
    # raise RuntimeError("This is a test error")
    return f"Finish with priority {priority}"


# @celery_signals.before_task_publish.connect(sender="spear_queue.tasks.spear_job")
# def handle_task_before_task_publish(
#     sender=None, headers: Any = None, body: dict[str, Any] = None, **_kwargs
# ):
#     logger.info(f"Task before task pubish: {headers=} {body=}")


@celery_signals.after_task_publish.connect(
    sender="spear_queue.tasks.spear_job"
)  # note sender is name for before/after task publish
def handle_task_after_task_publish(
    sender=None, headers: Any = None, body: dict[str, Any] = None, **_kwargs
):
    logger.info(f"Task after task pubish: {headers=} {body=}")
    spear_job = SpearJob.objects.create(
        priority=body[1]["priority"],
        celery_job_id=headers["id"],
        args=headers["argsrepr"],
        kwargs=headers["kwargsrepr"],
    )
    logger.info(f"After task publish handler: Created spear job: {spear_job=}")
    # payload = {
    #     "priority": body[1]["priority"],
    #     "celery_job_id": headers["id"],
    #     "args": headers["argsrepr"],
    #     "kwargs": headers["kwargsrepr"],
    # }
    # request_headers = {
    #     "accept": "application/json",
    #     "Content-Type": "application/json",
    # }
    # response = requests.post(
    #     "http://app:8080/api/spear_job/spear-jobs/",
    #     json=payload,
    #     headers=request_headers,
    # )
    # logger.info(
    #     f"Response after_task_publish: {response.status_code=} {response.text=}"
    # )


@celery_signals.task_prerun.connect(sender=spear_job)
def handle_task_prerun(
    task_id: str, task: Any, args: list[Any], kwargs: dict[str, Any], **_kwargs
):
    worker = os.environ.get("WORKER_NAME")
    logger.info(f"Task before task run: {task_id=}, {worker=}")

    payload = {
        "status": "RUNNING",
        "started_at": timezone.now().isoformat(),
        "worker_name": worker,
    }
    request_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.patch(
        f"http://app:8080/api/spear_job/spear-jobs/{task_id}/",
        json=payload,
        headers=request_headers,
    )
    logger.info(f"Response prerun: {response.status_code=} {response.text=}")


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
    worker = os.environ.get("WORKER_NAME")
    logger.info(f"Task after task run: {task_id=}, {state=}, {retval=}, {worker=}")
    if state == "SUCCESS":
        payload = {
            "status": state,
            "completed_at": timezone.now().isoformat(),
            "result": retval,
        }
    elif state == "FAILURE":
        payload = {
            "status": state,
            "completed_at": timezone.now().isoformat(),
            "error": str(retval),
        }

    request_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.patch(
        f"http://app:8080/api/spear_job/spear-jobs/{task_id}/",
        json=payload,
        headers=request_headers,
    )
    logger.info(f"Response postrun: {response.status_code=} {response.text=}")


@celery_signals.celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs):
    os.environ["WORKER_NAME"] = f"{sender}"
    logger.info(f"Worker name: {os.environ['WORKER_NAME']}")
