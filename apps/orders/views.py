from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.carts.models import ShoppingCart, CartItem
from apps.products.models import Product

class OrderViewSet(viewsets.ModelViewSet):
    """
    Comprehensive order management viewset
    
    Supports:
    - Create order from cart
    - List user orders
    - Retrieve specific order
    - Cancel pending orders
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
    @transaction.atomic
    def create_from_cart(self, request):
        try:
            cart, _ = ShoppingCart.objects.get_or_create(user=request.user)

            if not cart.cart_items.exists():
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            order = Order.objects.create(
                user=request.user,
                order_status='pending'
            )

            total_amount = 0

            for cart_item in cart.cart_items.all():
                product = cart_item.product
                if cart_item.quantity > product.stock_quantity:
                    raise ValidationError(
                        f'Insufficient stock for {product.name}. '
                        f'Available: {product.stock_quantity}, Requested: {cart_item.quantity}'
                    )

                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.price
                )

                product.stock_quantity -= cart_item.quantity
                product.save()

                total_amount += order_item.quantity * order_item.price

            order.total_amount = total_amount
            order.save()

            cart.cart_items.all().delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # TODO: Log error
            return Response(
                {'error': 'Unexpected error occurred while creating order'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def cancel_order(self, request, pk=None):
        """
        Cancel a pending order and restore product stocks
        """
        try:
            order = self.get_object()

            if order.order_status != 'pending':
                return Response(
                    {'error': 'Only pending orders can be cancelled'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            for order_item in order.items.all():
                product = order_item.product
                product.stock_quantity += order_item.quantity
                product.save()

            order.order_status = 'cancelled'
            order.save()

            serializer = self.get_serializer(order)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': 'Error cancelling order'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def order_summary(self, request):
        orders = self.get_queryset()
        summary = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(order_status='pending').count(),
            'completed_orders': orders.filter(order_status='delivered').count(),
            'total_spent': sum(order.total_amount for order in orders)
        }
        return Response(summary)