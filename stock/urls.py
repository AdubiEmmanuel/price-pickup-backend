from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerStockViewSet

router = DefaultRouter()
router.register(r'customer-stock', CustomerStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
