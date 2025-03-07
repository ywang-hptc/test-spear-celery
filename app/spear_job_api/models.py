from django.db import models


class SpearServerName(models.TextChoices):
    SPEAR_SERVER_A = "A", "SPEAR Server A"
    SPEAR_SERVER_B = "B", "SPEAR Server B"


class SpearJob(models.Model):
    """Model representing a Spear job."""

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=5)
    status = models.CharField(max_length=20, default="PENDING")
    result = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    celery_job_id = models.CharField(
        max_length=100,
        unique=True,
    )
    worker_name = models.CharField(max_length=100, null=True, blank=True)
    server_name = models.CharField(
        max_length=100, null=True, blank=True, choices=SpearServerName
    )
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.worker_name:
            self.server_name = ""

        elif "servera" in self.worker_name.lower():
            self.server_name = SpearServerName.SPEAR_SERVER_A

        elif "serverb" in self.worker_name.lower():
            self.server_name = SpearServerName.SPEAR_SERVER_B

        else:
            self.server_name = "Unknown Server"

        super().save(*args, **kwargs)
