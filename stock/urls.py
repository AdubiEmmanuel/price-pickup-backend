from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerStockViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'customer-stock', CustomerStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
