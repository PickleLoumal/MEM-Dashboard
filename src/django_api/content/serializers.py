from rest_framework import serializers
from .models import ContentCategory, ModalContent


class ContentCategorySerializer(serializers.ModelSerializer):
    """Content category serializer"""
    
    class Meta:
        model = ContentCategory
        fields = ['id', 'name', 'slug', 'description', 'is_active']


class ModalContentSerializer(serializers.ModelSerializer):
    """Modal content serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = ModalContent
        fields = [
            'id', 'modal_id', 'title', 'description', 'importance', 'source',
            'category', 'category_name', 'content_type', 'breakdown', 
            'is_active', 'priority', 'created_at', 'updated_at'
        ]
    
    def get_breakdown(self, obj):
        """Get breakdown items"""
        return obj.get_breakdown_items()
