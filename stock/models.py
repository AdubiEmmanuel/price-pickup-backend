from django.db import models
from competitors.choices import SKU_CATEGORY_CHOICES, SKU_SIZE_CHOICES


class CustomerStockEntry(models.Model):
    """
    One row per product recorded during a salesman's visit to a customer:
    what the customer currently has in stock, and how much they took in
    (restocked) since the last visit. The same customer+SKU accumulates
    multiple time-stamped rows over successive visits, which is what
    powers trend/velocity analysis on the dashboard.
    """

    SOURCE_CHOICES = [
        ('CSV', 'Imported from CSV'),
        ('FORM', 'Created from form'),
    ]

    customer_name = models.CharField(max_length=255, verbose_name='Customer Name')
    location = models.CharField(max_length=255, verbose_name='Location')

    sku_category = models.CharField(
        max_length=255,
        choices=SKU_CATEGORY_CHOICES,
        verbose_name='SKU Category',
        null=True,
        blank=True,
    )
    sku_size = models.CharField(
        max_length=255,
        choices=SKU_SIZE_CHOICES,
        verbose_name='SKU Size',
        null=True,
        blank=True,
    )
    # Free text, not constrained to BRAND_CHOICES - see competitors/models.py for why.
    brand = models.CharField(
        max_length=255,
        verbose_name='Brand',
        null=True,
        blank=True,
    )
    sku_name = models.CharField(max_length=255, verbose_name='SKU Name', null=True, blank=True)

    current_stock = models.PositiveIntegerField(
        verbose_name='Current Stock', null=True, blank=True
    )
    sales_in = models.PositiveIntegerField(
        verbose_name='Sales In (Stock Received)', null=True, blank=True
    )

    is_unilever = models.BooleanField(default=False, verbose_name='Is Unilever Product')

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='FORM')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_name', 'location']),
            models.Index(fields=['sku_category']),
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.sku_name or ''}"
