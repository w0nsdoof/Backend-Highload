# product/admin.py
from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock_quantity', 'is_available', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('category', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'price', 'stock_quantity')
        }),
        ('Status & Meta', {
            'fields': ('is_available', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
