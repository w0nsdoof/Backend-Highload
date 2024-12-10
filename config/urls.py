from rest_framework.routers import DefaultRouter

from django.contrib import admin
from django.urls import path, include

from apps.products.urls import router as products_router

router = DefaultRouter()
router.registry.extend(products_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('api/', include(router.urls)),   
]
