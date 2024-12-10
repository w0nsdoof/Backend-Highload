from rest_framework import serializers

from apps.products.serializers import ProductSerializer
from apps.authentication.serializers import UserSerializer

from .models import OrderItem, Order

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_status', 'total_amount', 'items', 'created_at', 'updated_at']
          
class OrderDetailSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class RemoveProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    
class AddProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
