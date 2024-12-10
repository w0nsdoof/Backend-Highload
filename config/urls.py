from rest_framework.routers import DefaultRouter

from django.contrib import admin
from django.urls import path, include

from apps.products.urls import router as products_router
from apps.carts.urls import router as carts_router
from apps.orders.urls import router as orders_router

router = DefaultRouter()

router.registry.extend(products_router.registry)
router.registry.extend(carts_router.registry)
router.registry.extend(orders_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('api/', include(router.urls)),   
]
