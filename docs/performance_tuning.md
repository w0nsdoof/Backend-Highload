I'll help you implement Redis caching for your Django REST Framework product views. First, let's set up Redis and the required packages, then implement caching for your product views.

1. First, install the required package:
```bash
pip install django-redis
```

2. Add Redis configuration to your settings.py:
```python:config/settings.py
# ... existing settings ...

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Cache time to live is 15 minutes (in seconds)
CACHE_TTL = 60 * 15
```

3. Now, let's modify your ProductViewSet to implement caching. Here are the changes needed:

```python:apps/products/views.py
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions, status

class ProductViewSet(viewsets.ModelViewSet):
    # ... existing attributes ...

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Create a cache key based on the product ID
        cache_key = f'product_{kwargs["pk"]}'
        
        # Try to get the cached data
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # If no cache exists, get the data and cache it
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, settings.CACHE_TTL)
        return response

    def perform_update(self, serializer):
        # Clear cache when product is updated
        instance = serializer.save()
        cache_key = f'product_{instance.pk}'
        cache.delete(cache_key)
        cache.delete('product_list')  # Clear the list cache as well

    def perform_destroy(self, instance):
        # Clear cache when product is deleted
        cache_key = f'product_{instance.pk}'
        cache.delete(cache_key)
        cache.delete('product_list')  # Clear the list cache as well
        super().perform_destroy(instance)
```

This implementation:

1. Uses `@cache_page` decorator for the list view (GET /api/products/)
2. Implements manual caching for individual products (GET /api/products/<id>/)
3. Automatically invalidates cache when products are updated or deleted
4. Sets a 15-minute TTL (Time To Live) for cached items

Key features:
- The list view is cached entirely based on the URL
- Individual products are cached with a key format of `product_<id>`
- Cache is automatically cleared when products are updated or deleted
- Uses Redis as the caching backend

Make sure Redis is running before testing the API. You can test if caching is working by:
1. Making an initial request (should be slower)
2. Making subsequent requests (should be much faster)
3. Updating a product (should clear the cache)
4. Making another request (should be slower again as cache rebuilds)
