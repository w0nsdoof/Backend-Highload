from django.urls import path
from .views import PaymentViewSet

urlpatterns = [
    path('api/payment/<int:order_id>/', PaymentViewSet.as_view()),  # For generating payment link
    path('api/payment/<uuid:token>/', PaymentViewSet.as_view()),   # For processing the unique link
]
