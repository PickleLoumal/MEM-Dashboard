# Django Admin Configuration for Content Management

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from .models import ContentCategory, ModalContent
import json


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'content_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def content_count(self, obj):
        count = obj.modalcontent_set.count()
        if count > 0:
            url = reverse('admin:content_modalcontent_changelist')
            return format_html(
                '<a href="{}?category={}" style="color: #0066cc;">{} items</a>',
                url, obj.id, count
            )
        return '0 items'
    content_count.short_description = "Content Count"


@admin.register(ModalContent)
class ModalContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'modal_id', 'category', 'content_type', 
                   'is_active', 'priority', 'updated_at', 'breakdown_preview']
    list_filter = ['category', 'content_type', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'modal_id', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    list_editable = ['is_active', 'priority']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('modal_id', 'title', 'category', 'content_type', 'priority')
        }),
        ('Content Details', {
            'fields': ('description', 'importance', 'source'),
            'classes': ('wide',)
        }),
        ('Structured Data', {
            'fields': ('breakdown_data', 'additional_info'),
            'classes': ('collapse', 'wide'),
            'description': 'Structured data stored in JSON format'
        }),
        ('Status Settings', {
            'fields': ('is_active',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        obj.set_current_user(request.user)
        super().save_model(request, obj, form, change)
        
        # Display success message
        if change:
            messages.success(request, f'Content "{obj.title}" has been successfully updated')
        else:
            messages.success(request, f'Content "{obj.title}" has been successfully created')
    
    def breakdown_preview(self, obj):
        if obj.breakdown_data:
            try:
                items = obj.get_breakdown_items()[:3]  # Show first 3 items
                if items:
                    preview = "<div style='font-size: 12px;'>"
                    for item in items:
                        label = item.get('label', '')
                        value = item.get('value', '')
                        preview += f"• {label}: {value}<br>"
                    
                    if len(obj.get_breakdown_items()) > 3:
                        preview += f"<span style='color: #666;'>... and {len(obj.get_breakdown_items()) - 3} more</span>"
                    preview += "</div>"
                    return mark_safe(preview)
                else:
                    return mark_safe('<span style="color: #666;">JSON format mismatch</span>')
            except Exception as e:
                return mark_safe(f'<span style="color: #d32f2f;">Data parsing error: {str(e)}</span>')
        return mark_safe('<span style="color: #999;">No breakdown data</span>')
    breakdown_preview.short_description = "Breakdown Preview"
    
    # Custom actions
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {count} content items', level=messages.SUCCESS)
    make_active.short_description = "Activate selected content"
    
    def make_inactive(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {count} content items', level=messages.SUCCESS)
    make_inactive.short_description = "Deactivate selected content"
