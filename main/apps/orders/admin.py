from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_status', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('order_status', 'created_at')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]
