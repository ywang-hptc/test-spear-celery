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
