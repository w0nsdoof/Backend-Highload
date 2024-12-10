from rest_framework.routers import DefaultRouter
from .views import ShoppingCartViewSet

router = DefaultRouter()
router.register(r'carts', ShoppingCartViewSet, basename='shoppingcart')

urlpatterns = router.urls