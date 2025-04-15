from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
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

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('reviews').all()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Search by name or description
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(
                description__icontains=search_query
            )
        
        return queryset.order_by('-created_at')
    
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

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):         
        if self.action == 'list':
            return Category.objects.filter(parent=None)
        return Category.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        existing_category = Category.objects.filter(name=serializer.validated_data['name']).first()
        if existing_category:
            return Response({
                'message': 'Category already exists', 
                'category': CategorySerializer(existing_category).data
            }, status=status.HTTP_200_OK)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in this category and its subcategories
        """
        category = self.get_object()
        
        # Get all subcategory IDs recursively
        category_ids = [category.id]
        
        def get_subcategories(parent_id):
            subcats = Category.objects.filter(parent_id=parent_id)
            for subcat in subcats:
                category_ids.append(subcat.id)
                get_subcategories(subcat.id)
        
        # Get all subcategories recursively
        get_subcategories(category.id)
        
        # Get products from this category and all subcategories
        products = Product.objects.filter(category_id__in=category_ids)
        
        # Apply pagination
        paginator = LimitOffsetPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        
        if paginated_products is not None:
            serializer = ProductSerializer(paginated_products, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """
        Get all subcategories (recursive) of this category
        """
        category = self.get_object()
        
        # Function to recursively get all subcategories
        def get_all_subcategories(parent_id):
            direct_subcats = Category.objects.filter(parent_id=parent_id)
            all_subcats = list(direct_subcats)
            
            for subcat in direct_subcats:
                all_subcats.extend(get_all_subcategories(subcat.id))
                
            return all_subcats
        
        subcategories = get_all_subcategories(category.id)
        serializer = CategorySerializer(subcategories, many=True)
        
        return Response(serializer.data)
        
    @method_decorator(cache_page(settings.CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        """
        Cached retrieval of category details
        """
        cache_key = f'category_{kwargs["pk"]}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, settings.CACHE_TTL)
        return response