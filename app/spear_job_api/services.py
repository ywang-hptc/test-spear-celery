from typing import Optional
from django.db import transaction
from .serializers import SpearJobCreateSerializer, SpearJobUpdateSerializer
from .models import SpearJob


@transaction.atomic
def create_spear_job(*, data: dict):
    """
    Service layer function to create a SpearJob using SpearJobCreateSerializer.
    Raises serializers.ValidationError on validation errors.
    """
    ser = SpearJobCreateSerializer(data=data)
    ser.is_valid(raise_exception=True)
    obj = ser.save()
    return obj


@transaction.atomic
def update_spear_job(
    *,
    spear_job_id: Optional[int] = None,
    celery_job_id: Optional[str] = None,
    data: dict
):
    """
    Service layer function to update a SpearJob using SpearJobUpdateSerializer.
    Either spear_job_id or celery_job_id must be provided to identify the job.
    Raises serializers.ValidationError on validation errors.
    """
    if spear_job_id is None and celery_job_id is None:
        raise ValueError("Provide either spear_job_id or celery_job_id.")

    if spear_job_id is not None:
        job = SpearJob.objects.select_for_update().get(pk=spear_job_id)
    else:
        job = SpearJob.objects.select_for_update().get(celery_job_id=celery_job_id)

    serializer = SpearJobUpdateSerializer(instance=job, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    job = serializer.save()
    return job


@transaction.atomic
def revoke_spear_job(
    *, spear_job_id: Optional[int] = None, celery_job_id: Optional[str] = None
):
    """
    Service layer function to revoke a SpearJob by setting its status to REVOKED.
    Either spear_job_id or celery_job_id must be provided to identify the job.
    Raises serializers.ValidationError on validation errors.
    """
    if spear_job_id is None and celery_job_id is None:
        raise ValueError("Provide either spear_job_id or celery_job_id.")

    if spear_job_id is not None:
        job = SpearJob.objects.select_for_update().get(pk=spear_job_id)
    else:
        job = SpearJob.objects.select_for_update().get(celery_job_id=celery_job_id)

    job.status = "REVOKED"
    job.save()
    return job
