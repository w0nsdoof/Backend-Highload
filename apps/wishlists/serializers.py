from rest_framework import serializers
from .models import Wishlist, WishlistItem
from apps.products.models import Product
from apps.products.serializers import ProductSerializer

class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product", write_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_id", "created_at"]

class WishlistSerializer(serializers.ModelSerializer):
    wishlist_items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "wishlist_items", "created_at", "updated_at"]
