from django.contrib import admin
from .models import CustomerStockEntry


@admin.register(CustomerStockEntry)
class CustomerStockEntryAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'location', 'sku_name', 'brand', 'current_stock', 'sales_in', 'created_at']
    list_filter = ['sku_category', 'sku_size', 'brand', 'is_unilever']
    search_fields = ['customer_name', 'location', 'sku_name', 'brand']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Customer', {
            'fields': ('customer_name', 'location')
        }),
        ('Product', {
            'fields': ('sku_name', 'sku_category', 'sku_size', 'brand', 'is_unilever')
        }),
        ('Stock', {
            'fields': ('current_stock', 'sales_in')
        }),
        ('Metadata', {
            'fields': ('source', 'created_at', 'updated_at')
        }),
    )
