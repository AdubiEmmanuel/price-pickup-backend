from rest_framework import serializers
from competitors.choices import SKU_CATEGORY_CHOICES, SKU_SIZE_CHOICES
from .models import Distributor, Customer, CustomerStockEntry


class DistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = [
            'id',
            'distributor_code',
            'distributor_name',
            'city',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    # Write with a distributor_code (what admins actually have on hand), not
    # the internal numeric Distributor id.
    distributor_code = serializers.CharField(write_only=True)
    distributor_name = serializers.CharField(source='distributor.distributor_name', read_only=True)
    city = serializers.CharField(source='distributor.city', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_code',
            'customer_name',
            'location',
            'distributor_code',
            'distributor_name',
            'city',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_distributor_code(self, value):
        # Resolved to the actual Distributor instance here so create()/update()
        # can use it directly.
        try:
            return Distributor.objects.get(distributor_code=value)
        except Distributor.DoesNotExist:
            raise serializers.ValidationError(f'No distributor with code "{value}". Add it first.')

    def validate(self, data):
        if not self.instance and not data.get('distributor_code'):
            raise serializers.ValidationError('Distributor Code is required')
        return data

    def create(self, validated_data):
        distributor = validated_data.pop('distributor_code', None)
        return Customer.objects.create(distributor=distributor, **validated_data)

    def update(self, instance, validated_data):
        distributor = validated_data.pop('distributor_code', None)
        if distributor is not None:
            instance.distributor = distributor
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


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
