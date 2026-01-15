from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AutomationTaskViewSet

app_name = "automation"

router = DefaultRouter()
router.register(r"tasks", AutomationTaskViewSet, basename="automation-tasks")

urlpatterns = [
    path("", include(router.urls)),
]
