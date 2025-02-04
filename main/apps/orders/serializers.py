from rest_framework import serializers

from apps.products.serializers import ProductSerializer

from .models import Order, OrderItem, Payment

class PaymentSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    time_remaining = serializers.DurationField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method', 
            'status', 'unique_token', 'expiration_time',
            'is_expired', 'time_remaining'
        ]
        read_only_fields = ['status', 'unique_token', 'expiration_time']
        
class PaymentConfirmationSerializer(serializers.Serializer):
    confirmation = serializers.BooleanField()

class PaymentMethodUpdateSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)

    class Meta:
        fields = ['payment_method']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product', 
            'quantity', 
            'price', 
            'subtotal',
            'created_at', 
            'updated_at',
            'is_in_stock'
        ]
        read_only_fields = fields

    def get_subtotal(self, obj):
        return obj.quantity * obj.price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    status_display = serializers.CharField(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 
            'user', 
            'order_status', 
            'total_amount', 
            'items', 
            'total_items',
            'created_at', 
            'updated_at',
            'payment',
            'status_display',
            'is_cancelable'
        ]
        read_only_fields = fields

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())