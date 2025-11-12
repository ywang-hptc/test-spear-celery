"""Serializers for the spear jobs API."""

from rest_framework import serializers
from . import models


class SpearJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a SpearJob."""

    raystation_system = serializers.SlugRelatedField(
        queryset=models.RayStationSystem.objects.all(), slug_field="system_name"
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


class SpearJobSerializer(serializers.ModelSerializer):
    """Serializer for the SpearJob model."""

    raystation_system_name = serializers.SlugRelatedField(
        queryset=models.RayStationSystem.objects.all(), slug_field="system_name"
    )

    class Meta:
        model = models.SpearJob
        fields = "__all__"
