import uuid

from django.db import models
from django.utils.timezone import now, timedelta

from apps.orders.models import Order


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'Credit Card', 'Credit Card'
        PAYPAL = 'PayPal', 'PayPal'
        BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'

    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices)
    status = models.CharField(max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    unique_token = models.UUIDField(default=uuid.uuid4, unique=True)
    expiration_time = models.DateTimeField(default=lambda: now() + timedelta(minutes=5))
