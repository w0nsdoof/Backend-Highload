from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from debug_toolbar.toolbar import debug_toolbar_urls

from apps.products.urls import router as products_router
from apps.carts.urls import router as carts_router
from apps.orders.urls import router as orders_router
from apps.wishlists.urls import router as wishlists_router
from apps.reviews.urls import router as reviews_router

router = DefaultRouter()
router.registry.extend(products_router.registry)
router.registry.extend(carts_router.registry)
router.registry.extend(orders_router.registry)
router.registry.extend(wishlists_router.registry)
router.registry.extend(reviews_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),    
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include(router.urls)),
    path('', include('django_prometheus.urls')),
] + debug_toolbar_urls() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)