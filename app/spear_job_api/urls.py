from django.urls import path, include
from rest_framework.routers import DefaultRouter


from . import views

router = DefaultRouter()
router.register("spear-jobs", views.SpearJobViewSet, basename="spearjob")
router.register("spear-workflows", views.SpearWorkflowViewSet, basename="spearworkflow")

app_name = "spear_job_api"

urlpatterns = [path("", include(router.urls))]
