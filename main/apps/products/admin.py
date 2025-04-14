from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock_quantity', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing and Stock', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
