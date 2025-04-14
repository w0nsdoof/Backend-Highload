from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'product', 'rating', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
