from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'price', 'subtotal')

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('unique_token', 'expiration_time', 'is_expired')
    fields = ('amount', 'payment_method', 'status', 'unique_token', 'expiration_time', 'is_expired')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_status', 'total_amount', 'created_at', 'is_cancelable')
    list_filter = ('order_status', 'created_at', 'is_cancelable')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentInline]
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order__order_status',)
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('subtotal',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_method', 'status', 'is_expired', 'expiration_time')
    list_filter = ('status', 'payment_method', 'is_expired')
    search_fields = ('order__id', 'unique_token')
    readonly_fields = ('unique_token', 'expiration_time', 'is_expired')
    date_hierarchy = 'created_at'
