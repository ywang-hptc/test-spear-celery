from django.contrib import admin
from . import models


# Register your models here.
class SpearJobAdmin(admin.ModelAdmin):
    list_display = (
        "patient_id",
        "created_at",
        "started_at",
        "completed_at",
        "priority",
        "status",
        "logs",
        "celery_job_id",
        "worker_name",
        "raystation_system__system_name",
        "latest_heartbeat",
    )
    readonly_fields = (
        "celery_job_id",
        "worker_name",
        "server_name",
        "latest_heartbeat",
    )
    list_filter = ["priority", "status", "server_name"]
    search_fields = [
        "celery_job_id",
        "worker_name",
        "server_name",
        "status",
        "priority",
    ]


class RayStationSystemAdmin(admin.ModelAdmin):
    list_display = ("system_name", "system_uid")
    search_fields = ["system_name", "system_uid"]


admin.site.register(models.SpearJob, SpearJobAdmin)
admin.site.register(models.RayStationSystem, RayStationSystemAdmin)
