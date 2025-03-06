"""Serializers for the spear jobs API."""

from rest_framework import serializers
from . import models


class SpearJobSerializer(serializers.ModelSerializer):
    """Serializer for the SpearJob model."""

    class Meta:
        model = models.SpearJob
        fields = "__all__"
