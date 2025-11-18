import re
from django.apps import apps
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as rest_framework_serializers
from django.shortcuts import get_object_or_404
from django.db import transaction
from .serializers import (
    SpearJobCreateSerializer,
    SpearJobDetailSerializer,
    SpearJobUpdateSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import models
from .services import create_spear_job, update_spear_job


class SpearJobViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Create a Spear job."""

    queryset = models.SpearJob.objects.all()
    lookup_field = "id"

    action_serializer_classes = {
        "create": SpearJobCreateSerializer,
        "update": SpearJobUpdateSerializer,
        "partial_update": SpearJobUpdateSerializer,
        "retrieve": SpearJobDetailSerializer,
        "list": SpearJobDetailSerializer,
        "by_celery_job_id": SpearJobDetailSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, SpearJobDetailSerializer)

    def perform_create(self, serializer):
        """Create a Spear job using the service layer."""
        create_spear_job(data=self.request.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="by-celery/(?P<celery_job_id>[0-9a-f-]+)",
    )
    def by_celery_job_id(self, request, celery_job_id=None):
        """Retrieve a Spear job by its celery job ID."""
        try:
            job = models.SpearJob.objects.get(celery_job_id=celery_job_id)
        except models.SpearJob.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        # ensure row lock during append to avoid lost updates
        self.get_object()  # fetches instance; DB transaction + save()
        return super().partial_update(request, *args, **kwargs)
