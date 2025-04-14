from django.contrib import admin
from .models import Wishlist, WishlistItem

class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ('product', 'added_at')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('total_items', 'created_at', 'updated_at')
    inlines = [WishlistItemInline]
    date_hierarchy = 'created_at'

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'wishlist', 'product', 'added_at')
    list_filter = ('wishlist__user', 'added_at')
    search_fields = ('wishlist__user__username', 'product__name')
    readonly_fields = ('added_at',)
