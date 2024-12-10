from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

router = DefaultRouter()
router.register(r"products/(?P<product_pk>[^/.]+)/reviews", ReviewViewSet, basename="reviews")

urlpatterns = router.urls
