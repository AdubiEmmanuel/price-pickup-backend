from django.db import migrations, models

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

def create_initial_products(apps, schema_editor):
    CompetitorPrice = apps.get_model('competitors', 'CompetitorPrice')
    products_data = [
        {'sku_code': '32797212', 'sku_name': 'KNORR BEEF BULK PACK 3X2KG', 'kd_case': 21505.85, 'brand': 'KNORR'},
        {'sku_code': '64401562', 'sku_name': 'KNORR BEEF BTF 14X50X8G', 'kd_case': 24186.55, 'brand': 'KNORR'},
        {'sku_code': '64401568', 'sku_name': 'KNORR CHICKEN BTF 14X50X8G', 'kd_case': 24995.49, 'brand': 'KNORR'},
        {'sku_code': '67300841', 'sku_name': 'KNORR CHICKEN POWDER FORTI 12X400G', 'kd_case': 17794.65, 'brand': 'KNORR'},
        {'sku_code': '67300844', 'sku_name': 'KNORR CHICKEN POWDER FORTI 6X800G', 'kd_case': 17873.98, 'brand': 'KNORR'},
        {'sku_code': '68137064', 'sku_name': 'KNORR BEEF BTF 40X12X8G', 'kd_case': 17534.11, 'brand': 'KNORR'},
        {'sku_code': '68137086', 'sku_name': 'KNORR CHICKEN BTF 40X12X8G', 'kd_case': 17601.62, 'brand': 'KNORR'},
        {'sku_code': '68291416', 'sku_name': 'KNORR CHICKEN NATURAL 20X25X8G', 'kd_case': 15763.80, 'brand': 'KNORR'},
        {'sku_code': '68291462', 'sku_name': 'KNORR BEEF NATURAL 20X25X8G', 'kd_case': 13943.18, 'brand': 'KNORR'},
        {'sku_code': '69578271', 'sku_name': 'KNORR CHICKEN 20X20X8G', 'kd_case': 15304.78, 'brand': 'KNORR'},
        {'sku_code': '69578306', 'sku_name': 'KNORR BEEF 20X20X8G', 'kd_case': 15437.86, 'brand': 'KNORR'},
        {'sku_code': '64797692', 'sku_name': 'ROYCO BEEF BULK 5X500X4G', 'kd_case': 28513.24, 'brand': 'ROYCO'},
        {'sku_code': '67568581', 'sku_name': 'ROYCO BEEF MANDARA 20X100X4G', 'kd_case': 24348.38, 'brand': 'ROYCO'},
        {'sku_code': '64864641', 'sku_name': 'PEPSODENT 3 PROTECT COMPL. 24X2X130G', 'kd_case': 48825.43, 'brand': 'PEPSODENT'},
        {'sku_code': '69654193', 'sku_name': 'PEPSODENT 3 PROTECTION COMPL. 50X130G', 'kd_case': 57452.30, 'brand': 'PEPSODENT'},
        {'sku_code': '69654198', 'sku_name': 'PEPSODENT 3 PROTECT NAT. WHITE 50X130G', 'kd_case': 48669.55, 'brand': 'PEPSODENT'},
        {'sku_code': '69654208', 'sku_name': 'PEPSODENT CAVITY FIGHTER 50 X 130G', 'kd_case': 46631.35, 'brand': 'PEPSODENT'},
        {'sku_code': '69655756', 'sku_name': 'PEPSODENT CAVITY FIGHTER 240X8.5G', 'kd_case': 10887.60, 'brand': 'PEPSODENT'},
        {'sku_code': '62768303', 'sku_name': 'PEPSODENT TRIPLE COMPL 72 X 35G', 'kd_case': 27941.40, 'brand': 'PEPSODENT'},
        {'sku_code': '62729974', 'sku_name': 'CLOSEUP TRIPLE FRESH REDHOT 72 X 35G', 'kd_case': 26895.73, 'brand': 'CLOSE UP'},
        {'sku_code': '62729982', 'sku_name': 'CLOSEUP TP TRIPLE FRESH RH 240 X 8.5G', 'kd_case': 10887.60, 'brand': 'CLOSE UP'},
        {'sku_code': '62768295', 'sku_name': 'CLOSEUP COMPLETE FRESH 72 X 35G', 'kd_case': 27941.40, 'brand': 'CLOSE UP'},
        {'sku_code': '64817465', 'sku_name': 'CLOSEUP TOOTHPASTE TRIPLE FRESH 4X8X175G', 'kd_case': 40131.90, 'brand': 'CLOSE UP'},
        {'sku_code': '68353982', 'sku_name': 'CLOSEUP COMPLETE FRESH PROTECT 48X40G', 'kd_case': 18627.60, 'brand': 'CLOSE UP'},
        {'sku_code': '69654190', 'sku_name': 'CLOSEUP COMP. FRESH PROTECT 36X130G', 'kd_case': 38195.74, 'brand': 'CLOSE UP'},
        {'sku_code': '69790460', 'sku_name': 'CLOSEUP TRIPLE FRESH REDHOT 50 X 130G', 'kd_case': 50875.45, 'brand': 'CLOSE UP'},
        {'sku_code': '69790471', 'sku_name': 'CLOSEUP TRIPLE FRESH RED HOT 50 X 90G', 'kd_case': 35478.23, 'brand': 'CLOSE UP'},
        {'sku_code': '69972153', 'sku_name': 'REXONA WM BRIGHT BOUQUET 4X6X50ML', 'kd_case': 31798.92, 'brand': 'REXONA'},
        {'sku_code': '69972162', 'sku_name': 'REXONA WOMEN SHOWER FRESH RO 4X6X50ML', 'kd_case': 31798.92, 'brand': 'REXONA'},
        {'sku_code': '69639541', 'sku_name': 'REXONA MEN DEO AER AP XTRA COOL 12X200ML', 'kd_case': 42757.05, 'brand': 'REXONA'},
        {'sku_code': '69972130', 'sku_name': 'REXONA MEN SPORT DEF RO 4X6X50ML', 'kd_case': 31798.92, 'brand': 'REXONA'},
        {'sku_code': '69975975', 'sku_name': 'REXONA MEN XTRACOOL RO 4X6X50ML', 'kd_case': 31798.92, 'brand': 'REXONA'},
        {'sku_code': '32050304', 'sku_name': 'VASELINE BLUESEAL ORIGNL PJ 24X12X50ML', 'kd_case': 144360.29, 'brand': 'VASELINE'},
        {'sku_code': '69983845', 'sku_name': 'VASELINE BLUESEAL ORIGNL PJ 4X(6X400ML).', 'kd_case': 69045.19, 'brand': 'VASELINE'},
        {'sku_code': '69983850', 'sku_name': 'VASELINE BLUESEAL ORIGNL PJ 6X(6X225ML).', 'kd_case': 66010.20, 'brand': 'VASELINE'},
        {'sku_code': '32797229', 'sku_name': 'PEARS BABY LOTION RELAUNCH 4X(10X200ML)', 'kd_case': 44000.00, 'brand': 'PEARS'},
        {'sku_code': '32797230', 'sku_name': 'PEARS BABY OIL RELAUNCH 4X(10X200ML)', 'kd_case': 61310.00, 'brand': 'PEARS'},
        {'sku_code': '67363284', 'sku_name': 'PEARS BABY JELLY 40X225G', 'kd_case': 77780.00, 'brand': 'PEARS'},
    ]
    
    for product in products_data:
        product['sku_category'] = determine_category(product['sku_name'])
        product['source'] = 'FORM'
        product['is_unilever'] = True
        
        # Set all market prices equal to kd_case
        case_price = product['kd_case']
        product.update({
            'wholesale_price': case_price,
            'open_market_price': case_price,
            'ng_price': case_price,
            'small_supermarket_price': case_price
        })
        
        CompetitorPrice.objects.create(**product)

def remove_all_data(apps, schema_editor):
    CompetitorPrice = apps.get_model('competitors', 'CompetitorPrice')
    CompetitorPrice.objects.all().delete()

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitorPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku_code', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='SKU Code')),
                ('sku_category', models.CharField(blank=True, choices=[('NUTRITION', 'NUTRITION'), ('ORAL CARE', 'ORAL CARE'), ('DEODORANT', 'DEODORANT'), ('SKIN CARE', 'SKIN CARE'), ('SALVORY', 'SALVORY')], max_length=255, null=True, verbose_name='SKU Category')),
                ('sku_size', models.CharField(blank=True, choices=[('BULK PACK', 'BULK PACK'), ('MID PACK', 'MID PACK'), ('REGULAR PACK', 'REGULAR PACK'), ('SMALL PACK', 'SMALL PACK'), ('POWDERS', 'POWDERS')], max_length=255, null=True, verbose_name='SKU Size')),
                ('sku_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='SKU Name')),
                ('brand', models.CharField(blank=True, choices=[('PEARS', 'PEARS'), ('VASELINE', 'VASELINE'), ('CLOSE UP', 'CLOSE UP'), ('PEPSODENT', 'PEPSODENT'), ('KNORR', 'KNORR'), ('ROYCO', 'ROYCO'), ('REXONA', 'REXONA')], max_length=255, null=True, verbose_name='Brand')),
                ('kd_case', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='KD Case')),
                ('kd_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='KD Unit')),
                ('kd_price_gram', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='KD Price/Gram')),
                ('wholesale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Wholesale Price')),
                ('open_market_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Open Market Price')),
                ('ng_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='NG Price')),
                ('small_supermarket_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Small Supermarket Price')),
                ('is_unilever', models.BooleanField(default=False, verbose_name='Is Unilever Product')),
                ('location', models.CharField(blank=True, max_length=255, null=True, verbose_name='Location')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source', models.CharField(choices=[('CSV', 'Imported from CSV'), ('FORM', 'Created from form')], default='FORM', max_length=10, verbose_name='Data Source')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(create_initial_products, remove_all_data),
    ]
