from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_subtotal',)
    fields = ('product', 'quantity', 'price', 'get_subtotal')
    
    def get_subtotal(self, obj):
        if obj and hasattr(obj, 'quantity') and hasattr(obj, 'price'):
            if obj.quantity is not None and obj.price is not None:
                return obj.quantity * obj.price
        return 0
    get_subtotal.short_description = 'Subtotal'

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('unique_token', 'expiration_time', 'is_expired')
    fields = ('amount', 'payment_method', 'status', 'unique_token', 'expiration_time', 'is_expired')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_status', 'total_amount', 'created_at')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    search_fields = ('id', 'user__username', 'user__email')
    list_filter = ('order_status', 'created_at')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, PaymentInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'get_subtotal')
    readonly_fields = ('get_subtotal',)
    search_fields = ('order__id', 'product__name')
    list_filter = ('order__order_status',)
    
    def get_subtotal(self, obj):
        if obj.quantity is not None and obj.price is not None:
            return obj.quantity * obj.price
        return 0
    get_subtotal.short_description = 'Subtotal'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_method', 'status', 'is_expired', 'expiration_time')
    readonly_fields = ('unique_token', 'expiration_time', 'is_expired')
    search_fields = ('order__id', 'unique_token')
    list_filter = ('status', 'payment_method')
    date_hierarchy = 'created_at'
