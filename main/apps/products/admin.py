from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    ordering = ['-created_at']
    autocomplete_fields = ['parent']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_available', 'created_at', 'image']
    search_fields = ['name', 'description']
    list_filter = ['category', 'created_at']
    ordering = ['-created_at']
    autocomplete_fields = ['category']
    readonly_fields = ['created_at', 'updated_at']
