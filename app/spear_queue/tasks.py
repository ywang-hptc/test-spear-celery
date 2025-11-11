import os
import time
import logging
from django.utils import timezone
import celery.signals as celery_signals
from celery import shared_task
from typing import Any
from spear_job_api.models import SpearJob
import requests

logger = logging.getLogger(__name__)


@shared_task(queue="spear_tasks")
def spear_job(
    raystation_system: str, priority: int, workflow_name: str, workflow_config: str
) -> None:
    logger.info(f"Creating a spear job...")
    logger.info(f"RayStation System: {raystation_system}")
    logger.info(f"Priority: {priority}")
    logger.info(f"Workflow Name: {workflow_name}")
    logger.info(f"Workflow Config: {workflow_config}")


@celery_signals.after_task_publish.connect(
    sender="spear_queue.tasks.spear_job"
)  # note sender is name for before/after task publish
def handle_task_after_task_publish(
    sender=None, headers: Any = None, body: dict[str, Any] = None, **_kwargs
):
    """After task publish signal handler to create a SpearJob entry in the database."""
    logger.info(f"Task after task pubish: {headers=} {body=}")
    spear_job = SpearJob.objects.create(
        priority=body[1]["priority"],
        celery_job_id=headers["id"],
        args=headers["argsrepr"],
        kwargs=headers["kwargsrepr"],
    )
    logger.info(f"After task publish handler: Created spear job: {spear_job=}")


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
        f"http://{os.environ["QUEUE_API_HOST"]}:{os.environ["QUEUE_API_PORT"]}/api/spear_job/spear-jobs/{task_id}/",
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
        f"http://{os.environ["QUEUE_API_HOST"]}:{os.environ["QUEUE_API_PORT"]}/api/spear_job/spear-jobs/{task_id}/",
        json=payload,
        headers=request_headers,
    )
    logger.info(f"Response postrun: {response.status_code=} {response.text=}")


@celery_signals.celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs):
    os.environ["WORKER_NAME"] = f"{sender}"
    logger.info(f"Worker name: {os.environ['WORKER_NAME']}")
