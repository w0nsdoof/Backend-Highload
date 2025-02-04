from rest_framework.exceptions import ValidationError

from django.db import models
from django.conf import settings

from apps.products.models import Product

class ShoppingCart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        return sum(item.total_price for item in self.cart_items.all())

    def clear(self):
        self.cart_items.all().delete()
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def clean(self):
        # Check if product is in stock
        if not self.product.is_in_stock():
            raise ValidationError("Product is out of stock")
        
        # Check if requested quantity exceeds available stock
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(f"Only {self.product.stock_quantity} items available")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

