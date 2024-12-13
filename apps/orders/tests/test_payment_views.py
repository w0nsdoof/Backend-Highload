import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils.timezone import now, timedelta
from apps.orders.models import Order, Payment
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def order(user):
    return Order.objects.create(
        user=user,
        order_status='pending',
        total_amount=100.00
    )

@pytest.fixture
def payment(order):
    return Payment.objects.create(
        order=order,
        amount=100.00,
        payment_method='Credit Card',
        status=Payment.PaymentStatus.PENDING
    )

@pytest.mark.django_db
class TestPaymentViewSet:
    def test_confirm_payment_success(self, client, payment):
        url = reverse('payment-confirm-payment', kwargs={'token': payment.unique_token})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.COMPLETED

    def test_confirm_expired_payment(self, client, payment):
        # Set payment as expired
        payment.expiration_time = now() - timedelta(hours=1)
        payment.save()
        
        url = reverse('payment-confirm-payment', kwargs={'token': payment.unique_token})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'Payment has expired' in response.data['error']

    def test_check_payment_status(self, client, payment):
        url = reverse('payment-check-payment', kwargs={'payment_id': payment.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Payment.PaymentStatus.PENDING
        assert response.data['amount'] == 100.00
        assert response.data['payment_method'] == 'Credit Card'

    def test_change_payment_method(self, client, payment):
        url = reverse('payment-change-payment-method', kwargs={'pk': payment.id})
        data = {'payment_method': 'PayPal'}
        response = client.patch(url, data, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.payment_method == 'PayPal'
