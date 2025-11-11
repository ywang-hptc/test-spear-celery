from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class SpearServer(models.TextChoices):
    """The available Spear server names. Those are
    unlikely to be changed so we hard code them here. It is
    also possible to make them a separate model if needed."""

    SP1 = "HPTC-RAY-SP01", "HPTC-RAY-SP01"
    SP2 = "HPTC-RAY-SP02", "HPTC-RAY-SP02"


class SpearJobStatus(models.TextChoices):
    """The available Spear job statuses."""

    PENDING = "PENDING", "Pending"
    RUNNING = "RUNNING", "Running"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class RayStationSystem(models.Model):
    """RayStation System name and its system uid"""

    system_name = models.CharField(max_length=100, unique=True)
    system_uid = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.system_name} ({self.system_uid})"

    class Meta:
        verbose_name = "RayStation System"
        verbose_name_plural = "RayStation Systems"


class SpearJob(models.Model):
    """Model representing a Spear job."""

    patient_id = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        null=False,
        blank=False,
        max_length=20,
        choices=SpearJobStatus.choices,
        default=SpearJobStatus.PENDING,
    )
    logs = models.TextField(null=True, blank=True)
    celery_job_id = models.CharField(
        max_length=100,
        unique=True,
    )
    worker_name = models.CharField(max_length=100, null=True, blank=True)
    server_name = models.CharField(
        max_length=100, null=True, blank=True, choices=SpearServer.choices
    )
    workflow_name = models.CharField(max_length=200, null=True, blank=True)
    workflow_config = models.JSONField(null=True, blank=True)
    latest_heartbeat = models.DateTimeField(null=True, blank=True)
    raystation_system = models.ForeignKey(
        RayStationSystem,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="spear_jobs",
    )
    priority = models.SmallIntegerField(
        default=5, validators=[MaxValueValidator(1), MinValueValidator(10)]
    )

    def save(self, *args, **kwargs):
        # update the server_name based on the worker that picks up the job
        if not self.worker_name:
            self.server_name = ""

        elif "sp1" in self.worker_name.lower():
            self.server_name = SpearServer.SP1

        elif "sp2" in self.worker_name.lower():
            self.server_name = SpearServer.SP2

        else:
            self.server_name = "Unknown Server"

        super().save(*args, **kwargs)
