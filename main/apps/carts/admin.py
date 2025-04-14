from django.contrib import admin
from .models import ShoppingCart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('product', 'quantity', 'total_price')

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'calculate_total', 'created_at')
    readonly_fields = ('total_items', 'calculate_total', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'total_price')
    readonly_fields = ('total_price',)
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart__user',)
