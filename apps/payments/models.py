from django.db import models

from apps.orders.models import Order

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), ('Bank Transfer', 'Bank Transfer')
    ])
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')
    ], default='Pending')

