from django.db import models

class CompetitorPrice(models.Model):
    SOURCE_CHOICES = [
        ('CSV', 'Imported from CSV'),
        ('FORM', 'Created from form'),
    ]
    
    SKU_CATEGORY_CHOICES = [
        ('CASE', 'CASE'),
        ('DEOS', 'DEOS'),
        ('NUTRITION', 'NUTRITION'),
        ('ORALS', 'ORALS'),
        ('SKIN CARE', 'SKIN CARE'),
        ('SALVORY', 'SALVORY'),
    ]

    SKU_SIZE_CHOICES = [
        ('BULK PACK', 'BULK PACK'),
        ('MID PACK', 'MID PACK'),
        ('REGULAR PACK', 'REGULAR PACK'),
        ('SMALL PACK', 'SMALL PACK'),
    ]

    MARKET_CHOICES = [
        ('OPEN_MARKET', 'Open Market'),
        ('NG', 'NG Market'),
        ('SMALL_SUPERMARKET', 'Small Supermarket'),
    ]

    sku_name = models.CharField(
        max_length=255,
        verbose_name='SKU Name',
        null=True,
        blank=True
    )
    
    sku_description = models.TextField(
        verbose_name='SKU Description',
        blank=True,
        null=True
    )
    
    sku_category = models.CharField(
        max_length=255,
        choices=SKU_CATEGORY_CHOICES,
        verbose_name='SKU Category'
    )
    
    sku_size_category = models.CharField(
        max_length=255,
        choices=SKU_SIZE_CHOICES,
        verbose_name='SKU Size Category'
    )

    market_type = models.CharField(
        max_length=50,
        choices=MARKET_CHOICES,
        verbose_name='Market Type'
    )

    selling_price_case = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Selling Price (Case)'
    )

    selling_price_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Selling Price (Unit)',
        default=0.00  # Added default value
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='FORM',
        verbose_name='Data Source'
    )

    def __str__(self):
        return f"{self.sku_name} - {self.sku_category}"

    class Meta:
        ordering = ['-created_at']








