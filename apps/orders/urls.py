from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('payment/<int:order_id>/', PaymentViewSet.as_view({'post': 'create'}), name='payment-create'),
    path('payment/<uuid:token>/', PaymentViewSet.as_view({'get': 'confirm_payment'}), name='payment-confirm'),
]