# Database Optimization

## Design Principles
The database design focuses on efficiency, scalability, and performance optimization.

### Normalized Database Design
- Adheres to 3rd Normal Form (3NF)
- Minimizes data redundancy
- Improves data integrity

### Indexing Strategies
```python
class CartItem(models.Model):
    class Meta:
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['created_at']),
        ]
```

### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'HOST': os.getenv('DB_REPLICA_HOST', 'localhost'),
        'PORT': os.getenv('DB_REPLICA_PORT', '5433'),
    }
}
```

### Optimization Techniques
1. **Prefetching Related Objects**
   ```python
   def get_queryset(self):
       return Order.objects.select_related('user', 'payment') \
           .prefetch_related('items__product') \
           .filter(user=self.request.user)
   ```

2. **Query Optimization**
   - Use `select_related()` for foreign key relationships
   - Use `prefetch_related()` for many-to-many and reverse foreign key relations
   - Implement database-level constraints

### Performance Benefits
- Reduced database load
- Faster query execution
- Improved scalability
- Enhanced data integrity