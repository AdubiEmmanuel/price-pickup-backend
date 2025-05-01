from rest_framework import serializers
from .models import CompetitorPrice

class CompetitorPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorPrice
        fields = [
            'id',
            'sku_name',
            'sku_description',
            'sku_category',
            'sku_size_category',
            'market_type',
            'selling_price_case',
            'selling_price_unit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation to ensure data consistency
        """
        required_fields = [
            'sku_name',
            'sku_category',
            'sku_size_category',
            'market_type',
            'selling_price_case',
            'selling_price_unit',
        ]
        
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field.replace('_', ' ').title()} is required")
        
        return data

    def create(self, validated_data):
        return CompetitorPrice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.sku_category = validated_data.get('sku_category', instance.sku_category)
        instance.sku_size_category = validated_data.get('sku_size_category', instance.sku_size_category)
        instance.gram_unit = validated_data.get('gram_unit', instance.gram_unit)
        instance.unit_pack = validated_data.get('unit_pack', instance.unit_pack)
        instance.gram_pack = validated_data.get('gram_pack', instance.gram_pack)
        instance.pack_case = validated_data.get('pack_case', instance.pack_case)
        instance.kd_case_price = validated_data.get('kd_case_price', instance.kd_case_price)
        instance.kd_unit_price = validated_data.get('kd_unit_price', instance.kd_unit_price)
        instance.kd_price_gram = validated_data.get('kd_price_gram', instance.kd_price_gram)
        instance.selling_price_case = validated_data.get('selling_price_case', instance.selling_price_case)
        instance.open_market_pack_price = validated_data.get('open_market_pack_price', instance.open_market_pack_price)
        instance.ng_pack_price = validated_data.get('ng_pack_price', instance.ng_pack_price)
        instance.small_supermarket_pack_price = validated_data.get('small_supermarket_pack_price', instance.small_supermarket_pack_price)
        
        instance.save()
        return instance



