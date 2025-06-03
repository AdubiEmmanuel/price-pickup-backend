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

    def validate_sku_category(self, value):
        """
        Validate SKU category against allowed choices
        """
        if value and value not in [choice[0] for choice in CompetitorPrice.SKU_CATEGORY_CHOICES]:
            raise serializers.ValidationError(f"Invalid category. Must be one of: {', '.join([choice[0] for choice in CompetitorPrice.SKU_CATEGORY_CHOICES])}")
        return value

    def validate_sku_size(self, value):
        """
        Validate SKU size against allowed choices
        """
        if value and value not in [choice[0] for choice in CompetitorPrice.SKU_SIZE_CHOICES]:
            raise serializers.ValidationError(f"Invalid size. Must be one of: {', '.join([choice[0] for choice in CompetitorPrice.SKU_SIZE_CHOICES])}")
        return value

    def validate(self, data):
        """
        Custom validation to ensure data consistency
        """
        # For new SKU creation, category and size are required
        if not self.instance:  # Creating new instance
            required_fields = ['sku_category', 'sku_size', 'sku_name']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field.replace('_', ' ').title()} is required for new SKU creation")

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
                brand=validated_data.get('brand', instance.brand),
                sku_category=validated_data.get('sku_category', instance.sku_category),
                sku_size=validated_data.get('sku_size', instance.sku_size),
                kd_case=validated_data.get('kd_case', instance.kd_case),
                kd_unit=validated_data.get('kd_unit', instance.kd_unit),
                kd_price_gram=validated_data.get('kd_price_gram', instance.kd_price_gram),
                wholesale_price=validated_data.get('wholesale_price', instance.wholesale_price),
                open_market_price=validated_data.get('open_market_price', instance.open_market_price),
                ng_price=validated_data.get('ng_price', instance.ng_price),
                small_supermarket_price=validated_data.get('small_supermarket_price', instance.small_supermarket_price),
                is_unilever=validated_data.get('is_unilever', instance.is_unilever),
                location=validated_data.get('location', instance.location),
                source='FORM'  # Mark as created from form
            )
            return new_instance

        # For records created from the form, update normally
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance








