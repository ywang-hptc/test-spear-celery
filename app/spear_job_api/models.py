from django.db import models


# Create your models here.
class SpearJob(models.Model):
    """Model representing a Spear job."""

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=5)
    status = models.CharField(max_length=20, default="PENDING")
    result = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    celery_job_id = models.CharField(max_length=100, null=True, blank=True)
    worker_name = models.CharField(max_length=100, null=True, blank=True)
    server_name = models.CharField(max_length=100, null=True, blank=True)
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.worker_name:
            self.server_name = ""

        elif "servera" in self.worker_name.lower():
            self.server_name = "SPEAR Server A"

        elif "serverb" in self.worker_name.lower():
            self.server_name = "SPEAR Server B"

        else:
            self.server_name = "Unknown Server"
        super().save(*args, **kwargs)
