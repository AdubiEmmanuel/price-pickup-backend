from django.core.management.base import BaseCommand
from competitors.models import CompetitorPrice

def determine_category(sku_name):
    if any(word in sku_name for word in ['KNORR', 'ROYCO']):
        return 'NUTRITION'
    elif any(word in sku_name for word in ['PEPSODENT', 'CLOSEUP']):
        return 'ORAL CARE'
    elif 'REXONA' in sku_name:
        return 'DEODORANT'
    elif any(word in sku_name for word in ['VASELINE', 'PEARS']):
        return 'SKIN CARE'
    return None

class Command(BaseCommand):
    help = 'Seeds the database with initial Unilever products'

    def handle(self, *args, **kwargs):
        products_data = [
            # All product data here...
            {
                'sku_code': '32797212',
                'sku_name': 'KNORR BEEF BULK PACK 3X2KG',
                'kd_case': 21505.85,
                'brand': 'KNORR',
                'is_unilever': True,
            },
            # ... rest of the products
        ]

        for product in products_data:
            product['sku_category'] = determine_category(product['sku_name'])
            product['source'] = 'FORM'
            
            try:
                CompetitorPrice.objects.create(**product)
                self.stdout.write(self.style.SUCCESS(f'Successfully created product {product["sku_name"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create product {product["sku_name"]}: {str(e)}'))
