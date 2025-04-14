from django.contrib import admin
from .models import ShoppingCart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'price', 'subtotal')

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('total_items', 'total_amount', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('cart__user',)
    search_fields = ('cart__user__username', 'product__name')
    readonly_fields = ('subtotal',)
