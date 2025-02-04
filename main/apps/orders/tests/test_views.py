import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.orders.models import Order, OrderItem, Payment
from apps.products.models import Product
from apps.carts.models import ShoppingCart, CartItem

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def product():
    return Product.objects.create(
        name='Test Product',
        price=10.00,
        stock_quantity=5
    )

@pytest.fixture
def cart(user):
    return ShoppingCart.objects.create(user=user)

@pytest.fixture
def cart_with_items(cart, product):
    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2
    )
    return cart

@pytest.mark.django_db
class TestOrderViewSet:
    def test_create_order_from_cart_success(self, authenticated_client, cart_with_items, user):
        url = reverse('orders:order-create-from-cart')
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1
        assert OrderItem.objects.count() == 1
        assert Payment.objects.count() == 1
        
        order = Order.objects.first()
        assert order.total_amount == 20.00
        assert order.order_status == 'pending'
        assert order.user == user

    def test_create_order_from_empty_cart(self, authenticated_client, cart):
        url = reverse('orders:order-create-from-cart')
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()
        assert response.json()['error'] == 'Cart is empty'

    def test_cancel_order_success(self, authenticated_client, cart_with_items):
        # First create an order
        create_url = reverse('orders:order-create-from-cart')
        create_response = authenticated_client.post(create_url)
        order_id = create_response.json()['order']['id']
        
        # Then cancel it
        cancel_url = reverse('orders:order-cancel-order', kwargs={'pk': order_id})
        response = authenticated_client.post(cancel_url)
        
        assert response.status_code == status.HTTP_200_OK
        order = Order.objects.get(id=order_id)
        assert order.order_status == 'cancelled'

    def test_order_summary(self, authenticated_client, cart_with_items):
        # Create an order first
        url = reverse('order-create-from-cart')
        authenticated_client.post(url)
        
        # Get order summary
        url = reverse('order-order-summary')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert response.data['summary']['total_orders'] == 1
        assert response.data['summary']['pending_orders'] == 1

    def test_confirm_payment(self, authenticated_client, cart_with_items):
        # Create an order first
        url = reverse('order-create-from-cart')
        response = authenticated_client.post(url)
        order_id = response.data['order']['id']
        
        # Confirm payment
        url = reverse('order-confirm-payment', kwargs={'pk': order_id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        order = Order.objects.get(id=order_id)
        assert order.order_status == 'shipped'
