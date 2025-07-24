from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentCategoryViewSet, ModalContentViewSet

router = DefaultRouter()
router.register(r'categories', ContentCategoryViewSet)
router.register(r'modals', ModalContentViewSet)

urlpatterns = [
    path('api/content/', include(router.urls)),
]
