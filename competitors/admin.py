from django.contrib import admin
from .models import CompetitorPrice

@admin.register(CompetitorPrice)
class CompetitorPriceAdmin(admin.ModelAdmin):
    list_display = ['sku_name', 'sku_category', 'sku_size_category', 'market_type', 'selling_price_case', 'selling_price_unit']
    list_filter = ['sku_category', 'sku_size_category', 'market_type']
    search_fields = ['sku_name', 'sku_description']
    readonly_fields = ['created_at', 'updated_at']
