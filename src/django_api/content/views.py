# Django REST Framework Views for Content Management

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import ModalContent, ContentCategory
from .serializers import ModalContentSerializer, ContentCategorySerializer
import logging

logger = logging.getLogger(__name__)


class ModalContentViewSet(viewsets.ReadOnlyModelViewSet):
    """Modal content API"""
    queryset = ModalContent.objects.filter(is_active=True)
    serializer_class = ModalContentSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        content_type = self.request.query_params.get('content_type')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if content_type:
            queryset = queryset.filter(content_type=content_type)
            
        return queryset.select_related('category').order_by('priority')
    
    @action(detail=False, methods=['get'])
    def by_modal_id(self, request):
        """Get content by modal_id"""
        modal_id = request.query_params.get('modal_id')
        if not modal_id:
            return Response({
                'error': 'modal_id parameter required',
                'message': 'Please provide modal_id parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get from cache
        cache_key = f'modal_content_{modal_id}'
        try:
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Getting content from cache: {modal_id}")
                return Response(cached_data)
        except:
            pass  # If cache is not available, continue to get from database
        
        try:
            content = ModalContent.objects.select_related('category').get(
                modal_id=modal_id, is_active=True
            )
            serializer = self.get_serializer(content)
            data = serializer.data
            
            # Cache for 1 hour
            try:
                cache.set(cache_key, data, 3600)
            except:
                pass  # If cache is not available, ignore
            
            logger.info(f"Getting content from database: {modal_id}")
            return Response(data)
            
        except ModalContent.DoesNotExist:
            logger.warning(f"Content not found: {modal_id}")
            return Response({
                'error': 'Content not found',
                'message': f'Content with ID {modal_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def all_content(self, request):
        """Get all content simplified version"""
        # Implement batch retrieval logic
        pass


class ContentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Content category API"""
    queryset = ContentCategory.objects.filter(is_active=True)
    serializer_class = ContentCategorySerializer
    permission_classes = [permissions.AllowAny]
