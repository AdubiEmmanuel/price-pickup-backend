from rest_framework import viewsets, status, permissions
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
    permission_classes = [permissions.AllowAny]  # Allow any user to access the API

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
        operation_description="Update a competitor price entry. If the entry is from CSV, a new record will be created instead.",
        request_body=CompetitorPriceSerializer,
        responses={200: CompetitorPriceSerializer}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # If the record is from CSV, we'll create a new one in the serializer
        # but we need to return a 201 Created status instead of 200 OK
        if instance.source == 'CSV':
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # For records created from the form, update normally
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a competitor price entry. If the entry is from CSV, a new record will be created instead.",
        request_body=CompetitorPriceSerializer,
        responses={200: CompetitorPriceSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # If the record is from CSV, we'll create a new one in the serializer
        # but we need to return a 201 Created status instead of 200 OK
        if instance.source == 'CSV':
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # For records created from the form, update normally
        return super().partial_update(request, *args, **kwargs)

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

    # Add a method to import CSV data and mark records as from CSV
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """
        Import competitor prices from CSV data.
        """
        # Your CSV import logic here
        # Make sure to set source='CSV' for all imported records
        
        return Response({"message": "CSV data imported successfully"}, status=status.HTTP_201_CREATED)



