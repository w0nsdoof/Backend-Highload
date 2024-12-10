from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ShoppingCart, CartItem
from .serializers import ShoppingCartSerializer, CartItemSerializer
from apps.products.models import Product

class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Comprehensive cart management viewset
    
    Supports:
    - Retrieve cart
    - Add/Remove items
    - Update quantities
    """
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ShoppingCart, CartItem
from .serializers import ShoppingCartSerializer, CartItemSerializer
from apps.products.models import Product

class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Comprehensive cart management viewset
    
    Supports:
    - Retrieve cart
    - Add/Remove items
    - Update quantities
    """
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle cart creation
        """
        # Ensure user is set
        serializer = self.get_serializer(data={'user': request.user.id})
        serializer.is_valid(raise_exception=True)
        
        # Create or retrieve cart
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        
        # Use the serializer of the existing or new cart
        serializer = self.get_serializer(cart)
        
        # Return appropriate status
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    @action(detail=False, methods=['GET'])
    def my_cart(self, request):
        """
        Retrieve or create user's cart
        """
        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check product availability
        if quantity > product.stock_quantity:
            return Response(
                {'error': f'Only {product.stock_quantity} items available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )

        # Update quantity if item already exists
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def update_item(self, request):
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')

        try:
            cart_item = CartItem.objects.get(
                id=cart_item_id, 
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check stock availability
        if quantity > cart_item.product.stock_quantity:
            return Response(
                {'error': f'Only {cart_item.product.stock_quantity} items available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove item if quantity is zero
        if quantity <= 0:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Update quantity
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=False, methods=['DELETE'])
    def remove_item(self, request):
        cart_item_id = request.data.get('cart_item_id')

        try:
            cart_item = CartItem.objects.get(
                id=cart_item_id, 
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Placeholder for future Order integration
# Order model would interact with Cart through a method like:
# def create_order_from_cart(cart):
#     order = Order.objects.create(user=cart.user)
#     for cart_item in cart.cart_items.all():
#         OrderItem.objects.create(
#             order=order,
#             product=cart_item.product,
#             quantity=cart_item.quantity,
#             price=cart_item.product.price
#         )
#     return order


