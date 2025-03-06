from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


from . import views

router = DefaultRouter()
router.register(
    "spear-jobs",
    views.SpearJobViewSet,
)
# TODO:  this is not added to swagger page?s
router.register(
    "test",
    views.SpearJobUpdateByCeleryIdView,
    basename="test",
)

app_name = "spear_job_api"

urlpatterns = [path("", include(router.urls))]
