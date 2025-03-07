from django.contrib import admin
from . import models


# Register your models here.
class SpearJobAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "started_at",
        "completed_at",
        "priority",
        "status",
        "result",
        "error",
        "celery_job_id",
        "worker_name",
        "server_name",
        "args",
        "kwargs",
    )
    readonly_fields = ("celery_job_id", "worker_name", "server_name")
    list_filter = ["priority", "status", "server_name"]
    search_fields = [
        "celery_job_id",
        "worker_name",
        "server_name",
        "status",
        "priority",
    ]


admin.site.register(models.SpearJob, SpearJobAdmin)
