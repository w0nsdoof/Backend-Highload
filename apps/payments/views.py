from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from .models import Payment, Order
from .serializers import PaymentSerializer

class PaymentViewSet(APIView):
    def post(self, request, order_id): #         Generate a unique payment URL and send it to the user's email.
        order = get_object_or_404(Order, id=order_id, user=request.user)

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method='Credit Card'  # TODO: give options
        )

        # Generate unique URL
        unique_url = f"{request.scheme}://{request.get_host()}/api/payment/{payment.unique_token}/"

        # Send email
        email = EmailMessage(
            subject="Complete Your Payment",
            body=f"Click the link to complete your payment: {unique_url}",
            to=[request.user.email]
        )
        email.send()

        return Response({"message": "Payment link sent to email."}, status=status.HTTP_201_CREATED)

    def get(self, request, token): #         Process the unique payment URL.
        payment = get_object_or_404(Payment, unique_token=token)

        # Check expiration
        if payment.expiration_time < now():
            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            return Response({"error": "Payment link expired."}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = Payment.PaymentStatus.COMPLETED
        payment.save()

        return Response({"message": "Payment completed successfully."}, status=status.HTTP_200_OK)
