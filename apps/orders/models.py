from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.products.models import Product  


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    order_status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Orders'

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

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

    def get_item_total(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(f"Insufficient stock for {self.product.name}")
        
        super().save(*args, **kwargs)