import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta

from apps.products.models import Product  

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['user', 'order_status'], name='order_user_status_idx'),
            models.Index(fields=['order_status', 'created_at'], name='order_status_date_idx'),
            models.Index(fields=['total_amount', 'created_at'], name='order_amount_date_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gte=0),
                name='order_total_amount_positive'
            )
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def calculate_total_amount(self):
        total = sum(item.get_item_total() for item in self.items.all())
        self.total_amount = total
        self.save()

    def create_from_cart(self, cart):
        if not cart.cart_items.exists():
            raise ValidationError("Cannot create order from an empty cart")

        for cart_item in cart.cart_items.all():
            # Check product availability
            if cart_item.product.stock_quantity < cart_item.quantity:
                raise ValidationError(f"Insufficient stock for product {cart_item.product.name}")

            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

            # Reduce product stock
            cart_item.product.stock_quantity -= cart_item.quantity
            cart_item.product.save()

        self.calculate_total_amount()
        cart.cart_items.all().delete()

        return self
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['user', 'order_status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['order_status', 'created_at']),
            models.Index(fields=['total_amount']),
        ]

    @property
    def is_cancelable(self):
        """Check if order can be cancelled based on status"""
        return self.order_status in ['pending', 'processing']

    @property
    def status_display(self):
        """Get human-readable status"""
        return dict(self.ORDER_STATUS_CHOICES)[self.order_status]

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Order Items'
        indexes = [
            models.Index(fields=['product'], name='orderitem_product_idx'),
            models.Index(fields=['order'], name='orderitem_order_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='orderitem_quantity_positive'
            ),
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name='orderitem_price_positive'
            )
        ]
        unique_together = [['order', 'product']]  # Prevent duplicate products in order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

    def get_item_total(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(f"Insufficient stock for {self.product.name}")
        
        super().save(*args, **kwargs)
        
    @property
    def subtotal(self):
        """Alias for get_item_total for consistency"""
        return self.get_item_total()

    @property
    def is_in_stock(self):
        """Check if product has sufficient stock"""
        return self.product.stock_quantity >= self.quantity

class Payment(models.Model):
    def default_expiration_time():
        return now() + timedelta(minutes=5)
    
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
    expiration_time = models.DateTimeField(default=default_expiration_time)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        indexes = [
            models.Index(fields=['status', 'created_at'], name='payment_status_created'),
            models.Index(fields=['unique_token'], name='payment_token_idx'),
            models.Index(fields=['expiration_time'], name='payment_expiration_idx'),
            models.Index(fields=['payment_method', 'status'], name='payment_method_status_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='payment_amount_positive'
            ),
            models.CheckConstraint(
                check=models.Q(expiration_time__gt=models.F('created_at')),
                name='payment_expiration_after_creation'
            )
        ]

    @property
    def is_expired(self):
        """Check if payment is expired"""
        return now() > self.expiration_time
    is_expired.fget.short_description = "Expired?"
    is_expired.fget.boolean = True

    @property
    def time_remaining(self):
        """Get remaining time before expiration"""
        if self.is_expired:
            return timedelta(0)
        return self.expiration_time - now()

    def mark_as_completed(self):
        """Mark payment as completed"""
        if self.status != self.PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be marked as completed")
        self.status = self.PaymentStatus.COMPLETED
        self.save()

    def mark_as_failed(self):
        """Mark payment as failed"""
        if self.status != self.PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be marked as failed")
        self.status = self.PaymentStatus.FAILED
        self.save()

    