from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from .models import Order, OrderItem

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop', price=1000.00, stock_quantity=10, category=self.category
        )
        self.client.login(username='testuser', password='password')

    def test_create_order(self):
        response = self.client.post('/orders/', {
            'order_status': 'Pending',
            'items': [{'product': self.product.id, 'quantity': 2, 'price': 1000.00}]
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
