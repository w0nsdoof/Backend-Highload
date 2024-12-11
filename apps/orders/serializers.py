from rest_framework import serializers

from apps.products.serializers import ProductSerializer

from .models import Order, OrderItem, Payment

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product', 
            'quantity', 
            'price', 
            'subtotal',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = fields

    def get_subtotal(self, obj):
        return obj.quantity * obj.price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()

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
            'updated_at'
        ]
        read_only_fields = fields

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'status', 'unique_token', 'expiration_time']

class PaymentConfirmationSerializer(serializers.Serializer):
    confirmation = serializers.BooleanField()