# wishlist/admin.py
from django.contrib import admin
from .models import Wishlist, WishlistItem

class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ('product',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    inlines = [WishlistItemInline]

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'wishlist', 'product', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('wishlist__user__username', 'product__name')
