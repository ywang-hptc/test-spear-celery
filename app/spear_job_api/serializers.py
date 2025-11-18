"""Serializers for the spear jobs API."""

from rest_framework import serializers
from . import models


class SpearJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a SpearJob."""

    raystation_system = serializers.SlugRelatedField(
        queryset=models.RayStationSystem.objects.all(),
        slug_field="system_name",
        write_only=True,
    )
    celery_job_id = serializers.UUIDField()
    print(raystation_system)

    class Meta:
        model = models.SpearJob
        fields = [
            "patient_id",
            "celery_job_id",
            "workflow_name",
            "workflow_config",
            "raystation_system",
            "priority",
        ]


class SpearJobDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a SpearJob."""

    raystation_system_name = serializers.SlugRelatedField(
        source="raystation_system",
        slug_field="system_name",
        read_only=True,
    )
    raystation_system_uid = serializers.SlugRelatedField(
        source="raystation_system",
        slug_field="system_uid",
        read_only=True,
    )

    class Meta:
        model = models.SpearJob
        fields = [
            "id",
            "patient_id",
            "created_at",
            "started_at",
            "completed_at",
            "status",
            "logs",
            "celery_job_id",
            "worker_name",
            "server_name",
            "workflow_name",
            "workflow_config",
            "latest_heartbeat",
            "raystation_system_name",
            "raystation_system_uid",
            "priority",
        ]
        read_only_fields = fields


class SpearJobUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a SpearJob."""

    append_log = serializers.CharField(
        write_only=True,
        required=False,
        help_text="A single log entry to append to the existing logs.",
    )
    append_logs = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="A list of log entries to append to the existing logs.",
    )

    class Meta:
        model = models.SpearJob
        fields = [
            "status",
            "started_at",
            "completed_at",
            "latest_heartbeat",
            "worker_name",
            "logs",
            "append_log",
            "append_logs",
        ]
        read_only_fields = ["logs"]

    def update(self, instance, validated_data):
        """Update a SpearJob, appending logs if provided."""
        append_log = validated_data.pop("append_log", None)
        append_logs = validated_data.pop("append_logs", None)

        # Append single log entry if provided
        if append_log:
            if instance.logs:
                instance.logs += f"\n{append_log}"
            else:
                instance.logs = append_log

        # Append multiple log entries if provided
        if append_logs:
            for log_entry in append_logs:
                if instance.logs:
                    instance.logs += f"\n{log_entry}"
                else:
                    instance.logs = log_entry

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        return super().update(instance, validated_data)
