from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.urls import router as products_router
from apps.carts.urls import router as carts_router
from apps.orders.urls import router as orders_router
from apps.wishlists.urls import router as wishlists_router
from apps.reviews.urls import router as reviews_router
from apps.orders.views import PaymentViewSet

router = DefaultRouter()
router.registry.extend(products_router.registry)
router.registry.extend(carts_router.registry)
router.registry.extend(orders_router.registry)
router.registry.extend(wishlists_router.registry)
router.registry.extend(reviews_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    
    path('api/', include(router.urls)),
    
    path('api/payment/<int:order_id>/', 
         PaymentViewSet.as_view({'post': 'create'}), 
         name='payment-create'),
    path('api/payment/<uuid:token>/', 
         PaymentViewSet.as_view({'get': 'confirm_payment'}), 
         name='payment-confirm'),
    path('api/payment/check_payments/', 
         PaymentViewSet.as_view({'get': 'check_payments'}), 
         name='payment-check'),
]