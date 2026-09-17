from rest_framework import serializers
from competitors.choices import SKU_CATEGORY_CHOICES, SKU_SIZE_CHOICES
from .models import Customer, CustomerStockEntry


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_code',
            'customer_name',
            'location',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class CustomerStockEntrySerializer(serializers.ModelSerializer):
    # Write with a customer_code (what salesmen/CSV rows actually have on hand),
    # not the internal numeric Customer id.
    customer_code = serializers.CharField(write_only=True)
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    location = serializers.CharField(source='customer.location', read_only=True)

    class Meta:
        model = CustomerStockEntry
        fields = [
            'id',
            'customer_code',
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

    def validate_customer_code(self, value):
        # Resolved to the actual Customer instance here so create() can use it
        # directly - validated_data['customer_code'] ends up holding a Customer,
        # not a string, by the time create() runs.
        try:
            return Customer.objects.get(customer_code=value)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f'No customer with code "{value}". Ask an admin to add it first.')

    def validate(self, data):
        if not self.instance:
            required_fields = ['customer_code', 'sku_category', 'sku_name']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(
                        f"{field.replace('_', ' ').title()} is required"
                    )
        return data

    def create(self, validated_data):
        customer = validated_data.pop('customer_code')
        return CustomerStockEntry.objects.create(customer=customer, **validated_data)
