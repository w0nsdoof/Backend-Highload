from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    @action(detail=False, methods=["POST"])
    def add_item(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if wishlist.wishlist_items.filter(product_id=product_id).exists():
            return Response({"error": "Product already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)

        item = WishlistItem.objects.create(wishlist=wishlist, product_id=product_id)
        serializer = WishlistItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["DELETE"])
    def remove_item(self, request):
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if not wishlist:
            return Response({"error": "Wishlist not found"}, status=status.HTTP_404_NOT_FOUND)

        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        item = wishlist.wishlist_items.filter(product_id=product_id).first()
        if not item:
            return Response({"error": "Product not in wishlist"}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)