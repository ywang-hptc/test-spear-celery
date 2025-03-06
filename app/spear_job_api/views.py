import re
from django.apps import apps
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as rest_framework_serializers
from django.shortcuts import get_object_or_404
from .serializers import SpearJobSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import models
from . import serializers


class SpearJobViewSet(viewsets.ModelViewSet):
    """Create a Spear job."""

    queryset = models.SpearJob.objects.all()
    serializer_class = serializers.SpearJobSerializer


class SpearJobUpdateByCeleryIdView(APIView):
    """Update a Spear job by Celery job ID."""

    queryset = models.SpearJob.objects.all()

    def get(self, request, celery_job_id):
        """Get a Spear job by Celery job ID."""
        spear_job = get_object_or_404(models.SpearJob, celery_job_id=celery_job_id)
        serializer = serializers.SpearJobSerializer(spear_job)
        return Response(serializer.data)

    def patch(self, request, celery_job_id):
        """Update a Spear job by Celery job ID."""
        spear_job = get_object_or_404(models.SpearJob, celery_job_id=celery_job_id)
        serializer = serializers.SpearJobSerializer(spear_job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_extra_actions():
        """Get extra actions."""
        return []
