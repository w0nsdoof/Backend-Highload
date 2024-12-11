from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import OrderViewSet,PaymentViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet,basename='order')
router.register(r'payments', PaymentViewSet,basename='payment')

urlpatterns = router.urls

payment_list = PaymentViewSet.as_view({
    'post': 'create',
})

payment_detail = PaymentViewSet.as_view({
    'get': 'confirm_payment',
})

urlpatterns = [
    path('payment/<int:order_id>/', payment_list, name='payment-create'),
    path('payment/<uuid:token>/', payment_detail, name='payment-confirm'),
]
