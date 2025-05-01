from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CompetitorPrice
from .serializers import CompetitorPriceSerializer

class CompetitorPriceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing competitor prices.
    
    Provides CRUD operations for competitor price data.
    """
    queryset = CompetitorPrice.objects.all()
    serializer_class = CompetitorPriceSerializer

    @swagger_auto_schema(
        operation_description="List all competitor prices",
        responses={200: CompetitorPriceSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new competitor price entry",
        request_body=CompetitorPriceSerializer,
        responses={201: CompetitorPriceSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific competitor price entry",
        responses={200: CompetitorPriceSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a competitor price entry",
        request_body=CompetitorPriceSerializer,
        responses={200: CompetitorPriceSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a competitor price entry",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_description="Get available category choices",
        responses={
            200: openapi.Response(
                description="Category choices",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'sku_categories': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'sku_size_categories': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'market_types': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def get_category_choices(self, request):
        """
        Get available choices for SKU categories, size categories, and market types.
        """
        return Response({
            'sku_categories': dict(CompetitorPrice.SKU_CATEGORY_CHOICES),
            'sku_size_categories': dict(CompetitorPrice.SKU_SIZE_CHOICES),
            'market_types': dict(CompetitorPrice.MARKET_CHOICES),
        })

