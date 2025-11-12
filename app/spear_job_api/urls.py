from django.urls import path, include
from rest_framework.routers import DefaultRouter


from . import views

router = DefaultRouter()
router.register("create", views.SpearJobCreateViewSet, basename="spearjob")


app_name = "spear_job_api"

urlpatterns = [path("", include(router.urls))]
