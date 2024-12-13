import redis
import simplejson as json
from celery import shared_task
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.orders.models import Order, OrderItem, Payment
from apps.products.models import Product

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@shared_task(bind=True)
def process_order_creation(self, user_id, cart_items):
    User = get_user_model()
    task_id = self.request.id
    try:
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            order_items = []
            total_amount = 0
            
            for item in cart_items:
                product = Product.objects.select_for_update().get(id=item['product_id'])
                
                if item['quantity'] > product.stock_quantity:
                    raise ValidationError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock_quantity}, Requested: {item['quantity']}"
                    )
                
                product.stock_quantity -= item['quantity']
                product.save()
                
                order_item_price = item['quantity'] * product.price
                total_amount += order_item_price
                
                order_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': product.price
                })

            order = Order.objects.create(user=user, order_status='pending', total_amount=total_amount)
            
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order, 
                    product=order_item['product'], 
                    quantity=order_item['quantity'], 
                    price=order_item['price']
                ) for order_item in order_items
            ])
            
            payment = Payment.objects.create(order=order, amount=total_amount, payment_method='Credit Card')
            
            # Store task result in Redis
            redis_client.set(task_id, json.dumps({
                'state': 'SUCCESS',
                'result': {
                    'order_id': order.id,
                    'total_amount': float(total_amount),
                    'payment_token': payment.unique_token
                }
            }, use_decimal=True))
            return {
                'order_id': order.id,
                'total_amount': float(total_amount),
                'payment_token': payment.unique_token
            }
            
    except Exception as e:
        redis_client.set(task_id, json.dumps({'state': 'FAILURE', 'error': str(e)}))
        raise e
