from django.db import models


# Create your models here.
class SpearJob(models.Model):
    """Model representing a Spear job."""

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    params = models.TextField()
    priority = models.IntegerField(default=5)
    status = models.CharField(max_length=20, default="PENDING")
    result = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    celery_job_id = models.CharField(max_length=100, null=True, blank=True)
