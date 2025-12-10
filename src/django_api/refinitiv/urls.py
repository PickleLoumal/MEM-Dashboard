# ==========================================
# Refinitiv URL Configuration
# ==========================================

from rest_framework.routers import DefaultRouter

from .views import RefinitivViewSet

router = DefaultRouter()
router.register(r"refinitiv", RefinitivViewSet, basename="refinitiv")

urlpatterns = router.urls

