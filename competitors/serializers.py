from rest_framework import serializers
from .models import CompetitorPrice

class CompetitorPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorPrice
        fields = [
            'id',
            'sku_category',
            'sku_size',
            'sku_name',
            'brand',
            'kd_case',
            'kd_unit',
            'kd_price_gram',
            'wholesale_price',
            'open_market_price',
            'ng_price',
            'small_supermarket_price',
            'is_unilever',
            'location',
            'source',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation to ensure data consistency
        """
        required_fields = [
            'sku_category',
            'sku_size',
        ]
        
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field.replace('_', ' ').title()} is required")
        
        return data

    def update(self, instance, validated_data):
        """
        Update and return an existing CompetitorPrice instance,
        or create a new one if the source is CSV
        """
        # If the record is from CSV, create a new record instead of updating
        if instance.source == 'CSV':
            # Create a new record with the same data as the CSV record
            # but mark it as coming from the form
            new_instance = CompetitorPrice.objects.create(
                sku_name=validated_data.get('sku_name', instance.sku_name),
                sku_description=validated_data.get('sku_description', instance.sku_description),
                sku_category=validated_data.get('sku_category', instance.sku_category),
                sku_size_category=validated_data.get('sku_size_category', instance.sku_size_category),
                market_type=validated_data.get('market_type', instance.market_type),
                selling_price_case=validated_data.get('selling_price_case', instance.selling_price_case),
                selling_price_unit=validated_data.get('selling_price_unit', instance.selling_price_unit),
                source='FORM'  # Mark as created from form
            )
            return new_instance
        
        # For records created from the form, update normally
        instance.sku_name = validated_data.get('sku_name', instance.sku_name)
        instance.sku_description = validated_data.get('sku_description', instance.sku_description)
        instance.sku_category = validated_data.get('sku_category', instance.sku_category)
        instance.sku_size_category = validated_data.get('sku_size_category', instance.sku_size_category)
        instance.market_type = validated_data.get('market_type', instance.market_type)
        instance.selling_price_case = validated_data.get('selling_price_case', instance.selling_price_case)
        instance.selling_price_unit = validated_data.get('selling_price_unit', instance.selling_price_unit)
        
        instance.save()
        return instance








