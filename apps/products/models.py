from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='products'
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
    
    def is_in_stock(self):
        return self.stock_quantity > 0