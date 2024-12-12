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
from .serializers import (
    OrderSerializer, OrderItemSerializer, 
    PaymentSerializer, PaymentConfirmationSerializer, PaymentMethodUpdateSerializer
)


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
        return Order.objects.select_related('user', 'payment').prefetch_related('items__product').filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
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
                {'error': 'Unexpected error occurred while creating order',
                 "log": str(e)}, 
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
        summary = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(order_status='pending').count(),
            'completed_orders': orders.filter(order_status='delivered').count(),
            'total_spent': sum(order.total_amount for order in orders)
        }
        return Response({
            'orders': serializer.data,
            'summary': summary
        })

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
          
class PaymentViewSet(viewsets.ViewSet):
    """
    A ViewSet to handle payments for orders, including:
    - Generating payment links
    - Sending payment links via email
    - Confirming payments
    - Marking payments as failed after expiration
    - Changing payment methods
    """
       
    @action(detail=False, methods=['get'], url_path='confirm/(?P<token>[^/.]+)')
    def confirm_payment(self, request, token):
        payment = get_object_or_404(Payment, unique_token=token)

        if payment.is_expired:
            time_delta = now() - payment.expiration_time
            return Response({
                "error": "Payment has expired",
                "time_expired": {
                    "seconds": int(time_delta.total_seconds()),
                    "minutes": int(time_delta.total_seconds() / 60),
                    "hours": int(time_delta.total_seconds() / 3600)
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment.mark_as_completed()
            return Response({
                "status": "Payment completed successfully",
                "order_id": payment.order.id
            })
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='check_payment/(?P<payment_id>[^/.]+)')
    def check_payment(self, request, payment_id=None):
        payment = get_object_or_404(Payment, pk=payment_id)
        time_delta = payment.time_remaining if not payment.is_expired else (now() - payment.expiration_time)
        
        time_info = {
            "seconds": int(time_delta.total_seconds()),
            "minutes": int(time_delta.total_seconds() / 60),
            "hours": int(time_delta.total_seconds() / 3600)
        }
        
        return Response({
            "order_id": payment.order.id,
            "status": payment.status,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "is_expired": payment.is_expired,
            "time_info": {
                "status": "expired" if payment.is_expired else "active", 
                "description": f"Expired {time_info['minutes']} minutes ago" if payment.is_expired else f"Active for {time_info['minutes']} more minutes",
                "time_values": time_info
            }
        })
        
    @action(detail=True, methods=['PATCH'])
    def change_payment_method(self, request, pk=None):  
        try:
            payment = get_object_or_404(Payment, pk=pk)
            order = payment.order
            
            # Check if order is in a state where payment can be changed
            if order.order_status not in ['pending', 'PAYMENT_FAILED']:
                return Response(
                    {'error': 'Cannot change payment method for this order status'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate the new payment method using serializer
            serializer = PaymentMethodUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update payment method
            payment.payment_method = serializer.validated_data['payment_method']
            payment.save()

            return Response({
                'message': 'Payment method updated successfully',
                'payment_method': payment.payment_method,
                'order_id': order.id
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
