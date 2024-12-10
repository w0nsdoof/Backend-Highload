from rest_framework import serializers
from .models import ShoppingCart, CartItem
from apps.products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'product', 
            'quantity', 
            'subtotal', 
            'created_at', 
            'updated_at'
        ]

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price

class ShoppingCartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = [
            'id', 
            'user', 
            'cart_items', 
            'total_items', 
            'total_price', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['user', 'id', 'created_at', 'updated_at']

    def get_total_items(self, obj):
        # Handle both model instance and dictionary
        if isinstance(obj, dict):
            return 0
        return sum(item.quantity for item in obj.cart_items.all())

    def get_total_price(self, obj):
        # Handle both model instance and dictionary
        if isinstance(obj, dict):
            return 0.00
        return sum(item.quantity * item.product.price for item in obj.cart_items.all())

    def create(self, validated_data):
        """
        Custom create method to handle cart creation
        """
        # Remove cart_items if present in validated_data
        validated_data.pop('cart_items', None)
        
        # Check if user already has a cart
        user = validated_data.get('user')
        if user:
            existing_cart = ShoppingCart.objects.filter(user=user).first()
            if existing_cart:
                return existing_cart
        
        # Create new cart
        return super().create(validated_data)