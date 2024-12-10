from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock_quantity', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'created_at')
