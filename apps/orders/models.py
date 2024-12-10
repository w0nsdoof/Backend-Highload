from django.db import models
from django.conf import settings

from apps.products.models import Product


class Order(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        CREATED = "CREATED", "Created"
        PAID = "PAID", "Paid"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        FINISHED = 'FINISHED', 'Finished'
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['status'])
        ]
    
    def calculate_total(self):
        total = sum(item.quantity * item.price for item in self.items.all())
        self.total_amount = total
        self.save()
        
    def change_status(self, new_status):
        self.status = new_status
        self.save()

    def add_product(self, product, quantity=1):
        if self.status != Order.STATUS_CHOICES.CREATED:
            raise ValueError("Unable to alter the order because it is no longer in 'CREATED' status")
        
        # Check product availability
        if product.quantity < quantity:
            raise ValueError(f"Not enough stock for {product.name}. Available: {product.quantity}, Requested: {quantity}")
        
        # Check if product already exists in order
        order_item, created = self.items.get_or_create(product=product, defaults={'quantity': 0, 'price': product.price})
        
        # Update the quantity and check the total again
        if order_item.quantity + quantity > product.quantity:
            raise ValueError(f"Adding this amount exceeds available stock for {product.name}. Available: {product.quantity}, Requested: {order_item.quantity + quantity}")
        
        order_item.quantity += quantity
        order_item.save()

        # Update the total amount
        self.total_amount += order_item.price * quantity
        self.save()

    def remove_product(self, product, quantity=1):
        if self.status != Order.STATUS_CHOICES.CREATED:
            raise ValueError("Unable to alter the order because it is no longer in 'CREATED' status")
        
        order_item = self.items.filter(product=product).first()
        if not order_item:
            raise ValueError("Product not in order.")

        if order_item.quantity <= quantity: # remove order item (убрать товар)
            self.total_amount -= order_item.price * order_item.quantity
            order_item.delete()
        else:
            order_item.quantity -= quantity # remove quantity of orderitem (убавить количество товара)
            self.total_amount -= order_item.product.price * quantity
            order_item.save()

        self.save()

    def remove_all_products(self):
        if self.status != Order.STATUS_CHOICES.CREATED:
            raise ValueError("Unable to alter the order because it is no longer in 'CREATED' status")
        
        for order_item in self.items.all():
            self.total_amount -= order_item.product.price * order_item.quantity
            order_item.delete()

        self.save()

    def process_payment(self):
        if self.status != Order.STATUS_CHOICES.CREATED:
            raise ValueError("Unable to alter the order because it is no longer in 'CREATED' status")
        if self.total_amount == 0:
            raise ValueError("No items in cart")

        # TODO: Logic for Payment 
        self.change_status(Order.STATUS_CHOICES.PAID)
        self.ship_order() # TODO: workaround for testing

    def ship_order(self):
        if self.status != Order.STATUS_CHOICES.PAID:
            raise ValueError("Unable to ship this order, status should be 'PAID'")
        
        self.change_status(Order.STATUS_CHOICES.SHIPPED)
        
        # Logic for delivery
        
        self.change_status(Order.STATUS_CHOICES.DELIVERED)
        
    def finish_order(self):
        if self.status != Order.STATUS_CHOICES.DELIVERED:
            raise ValueError("Unable to ship this order, status should be 'DELEVIRED'")

        self.change_status(Order.STATUS_CHOICES.FINISHED)

    def cancel_order(self):
        if self.status != Order.STATUS_CHOICES.CREATED:
            self.change_status(Order.STATUS_CHOICES.CANCELLED)
        else:
            raise ValueError("Unable to cancel this order, past point of no return")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_amount(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        self.price = self.product.price 
        super().save(*args, **kwargs)  
    
    