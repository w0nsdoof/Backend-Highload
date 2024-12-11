from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from apps.carts.models import ShoppingCart, CartItem
from apps.products.models import Product
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Comprehensive order and payment management viewset.
    
    Supports:
    - Create order from cart
    - List user orders
    - Retrieve specific order
    - Cancel pending orders
    - Process payment and confirmation
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve orders belonging to the authenticated user.
        """
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

            payment = Payment.objects.create(
                order=order,
                amount=total_amount,
                payment_method='Credit Card'  # TODO: give options
            )

            unique_url = f"{request.scheme}://{request.get_host()}/api/payment/{payment.unique_token}/"

            # Async method
            email = EmailMessage(
                subject="Complete Your Payment",
                body=f"Click the link to complete your payment: {unique_url}",
                to=[request.user.email]
            )
            email.send()

            cart.cart_items.all().delete()

            serializer = self.get_serializer(order)
            # TODO: only for development phase
            return Response(
                {
                    "order": serializer.data,
                    "payment_url": unique_url
                }, 
                status=status.HTTP_201_CREATED
            )

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
        try:
            order = self.get_object()

            if order.order_status == 'cancelled':
                return Response(
                    {'error': 'Order has already been cancelled'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
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
        """
        Provide a summary of the user's orders.
        """
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        try:
            payment = get_object_or_404(Payment, order=order)

            if payment.expiration_time < now():
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                return Response({"error": "Payment link expired."}, status=status.HTTP_400_BAD_REQUEST)

            payment.status = Payment.PaymentStatus.COMPLETED
            payment.save()

            # Update order status
            order.order_status = 'completed'
            order.save()

            return Response({"message": "Payment completed successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Error processing payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        orders = self.get_queryset()
        summary = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(order_status='pending').count(),
            'completed_orders': orders.filter(order_status='delivered').count(),
            'total_spent': sum(order.total_amount for order in orders)
        }
        return Response(summary)