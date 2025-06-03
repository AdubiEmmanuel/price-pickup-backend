from django.db import models

class CompetitorPrice(models.Model):
    SOURCE_CHOICES = [
        ('CSV', 'Imported from CSV'),
        ('FORM', 'Created from form'),
    ]
    
    SKU_CATEGORY_CHOICES = [
        ('NUTRITION', 'NUTRITION'),
        ('ORAL CARE', 'ORAL CARE'),
        ('DEODORANT', 'DEODORANT'),
        ('SKIN CARE', 'SKIN CARE'),
        ('SALVORY', 'SALVORY'),
    ]

    SKU_SIZE_CHOICES = [
        ('BULK PACK', 'BULK PACK'),
        ('MID PACK', 'MID PACK'),
        ('REGULAR PACK', 'REGULAR PACK'),
        ('SMALL PACK', 'SMALL PACK'),
        ('POWDERS', 'POWDERS'),
    ]

    MARKET_CHOICES = [
        ('OPEN_MARKET', 'Open Market'),
        ('NG', 'NG Market'),
        ('SMALL_SUPERMARKET', 'Small Supermarket'),
        ('WHOLESALE', 'Wholesale'),
    ]

    # Basic SKU information
    sku_category = models.CharField(
        max_length=255,
        choices=SKU_CATEGORY_CHOICES,
        verbose_name='SKU Category',
        null=True,
        blank=True
    )

    sku_size = models.CharField(
        max_length=255,
        choices=SKU_SIZE_CHOICES,
        verbose_name='SKU Size',
        null=True,
        blank=True
    )
    
    sku_name = models.CharField(
        max_length=255,
        verbose_name='SKU Name',
        null=True,
        blank=True
    )
    
    brand = models.CharField(
        max_length=255,
        verbose_name='Brand',
        blank=True,
        null=True
    )
    
    # Price information
    kd_case = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='KD Case',
        null=True,
        blank=True
    )
    
    kd_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='KD Unit',
        null=True,
        blank=True
    )
    
    kd_price_gram = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='KD Price/Gram',
        null=True,
        blank=True
    )
    
    # Market prices
    wholesale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Wholesale Price',
        null=True,
        blank=True
    )
    
    open_market_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Open Market Price',
        null=True,
        blank=True
    )
    
    ng_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='NG Price',
        null=True,
        blank=True
    )
    
    small_supermarket_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Small Supermarket Price',
        null=True,
        blank=True
    )
    
    # Additional fields
    is_unilever = models.BooleanField(
        default=False,
        verbose_name='Is Unilever Product'
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name='Location',
        blank=True,
        null=True
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
        return f"{self.sku_name or ''} - {self.sku_category or ''}"

    class Meta:
        ordering = ['-created_at']











