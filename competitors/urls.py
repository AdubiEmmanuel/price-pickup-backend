from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitorPriceViewSet

router = DefaultRouter()
router.register(r'competitor-prices', CompetitorPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]




