from django.contrib import admin
from .models import Customer, CustomerStockEntry


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'customer_name', 'location', 'created_at']
    search_fields = ['customer_code', 'customer_name', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CustomerStockEntry)
class CustomerStockEntryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'sku_name', 'brand', 'current_stock', 'sales_in', 'created_at']
    list_filter = ['sku_category', 'sku_size', 'brand', 'is_unilever']
    search_fields = ['customer__customer_name', 'customer__customer_code', 'customer__location', 'sku_name', 'brand']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Customer', {
            'fields': ('customer',)
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
