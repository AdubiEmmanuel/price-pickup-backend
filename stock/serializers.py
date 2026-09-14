from rest_framework import serializers
from competitors.choices import SKU_CATEGORY_CHOICES, SKU_SIZE_CHOICES
from .models import CustomerStockEntry


class CustomerStockEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerStockEntry
        fields = [
            'id',
            'customer_name',
            'location',
            'sku_category',
            'sku_size',
            'brand',
            'sku_name',
            'current_stock',
            'sales_in',
            'is_unilever',
            'source',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_sku_category(self, value):
        valid = [choice[0] for choice in SKU_CATEGORY_CHOICES]
        if value and value not in valid:
            raise serializers.ValidationError(f"Invalid category. Must be one of: {', '.join(valid)}")
        return value

    def validate_sku_size(self, value):
        valid = [choice[0] for choice in SKU_SIZE_CHOICES]
        if value and value not in valid:
            raise serializers.ValidationError(f"Invalid size. Must be one of: {', '.join(valid)}")
        return value

    def validate(self, data):
        if not self.instance:
            required_fields = ['customer_name', 'location', 'sku_category', 'sku_name']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(
                        f"{field.replace('_', ' ').title()} is required"
                    )
        return data
