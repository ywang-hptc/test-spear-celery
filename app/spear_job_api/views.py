import re
from django.apps import apps
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as rest_framework_serializers
from django.shortcuts import get_object_or_404
from . import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import models
from . import serializers


class SpearJobViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Create a Spear job."""

    queryset = models.SpearJob.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):  # read-only actions
            return serializers.SpearJobDetailSerializer

        # For create and update actions
        return serializers.SpearJobCreateSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="by-celery/(?P<celery_job_id>[0-9a-f-]+)",
    )
    def by_celery_job_id(self, request, celery_job_id=None):
        try:
            job = models.SpearJob.objects.get(celery_job_id=celery_job_id)
        except models.SpearJob.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(job)
        return Response(serializer.data)


# class SpearJobViewSet(
#     mixins.CreateModelMixin,
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     viewsets.GenericViewSet,
# ):
#     """Create a Spear job."""

#     queryset = models.SpearJob.objects.all()
#     serializer_class = serializers.SpearJobSerializer
#     lookup_field = "celery_job_id"

#     def partial_update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
