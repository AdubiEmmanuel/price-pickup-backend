from django.contrib import admin
from .models import CompetitorPrice

@admin.register(CompetitorPrice)
class CompetitorPriceAdmin(admin.ModelAdmin):
    list_display = ['sku_name', 'sku_category', 'sku_size', 'brand', 'kd_case', 'kd_unit']
    list_filter = ['sku_category', 'sku_size', 'brand', 'is_unilever']
    search_fields = ['sku_name', 'brand']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku_name', 'sku_category', 'sku_size', 'brand', 'is_unilever', 'location')
        }),
        ('Price Information', {
            'fields': ('kd_case', 'kd_unit', 'kd_price_gram')
        }),
        ('Market Prices', {
            'fields': ('wholesale_price', 'open_market_price', 'ng_price', 'small_supermarket_price')
        }),
        ('Metadata', {
            'fields': ('source', 'created_at', 'updated_at')
        }),
    )

