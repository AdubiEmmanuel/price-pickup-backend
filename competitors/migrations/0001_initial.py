from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitorPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku_category', models.CharField(choices=[('CASE', 'CASE'), ('DEOS', 'DEOS'), ('NUTRITION', 'NUTRITION'), ('ORALS', 'ORALS'), ('SKIN CARE', 'SKIN CARE'), ('SALVORY', 'SALVORY')], max_length=255, verbose_name='SKU Category')),
                ('sku_size_category', models.CharField(choices=[('BULK PACK', 'BULK PACK'), ('MID PACK', 'MID PACK'), ('REGULAR PACK', 'REGULAR PACK'), ('SMALL PACK', 'SMALL PACK')], max_length=255, verbose_name='SKU Size Category')),
                ('market_type', models.CharField(choices=[('OPEN_MARKET', 'Open Market'), ('NG', 'NG Market'), ('SMALL_SUPERMARKET', 'Small Supermarket')], max_length=50, verbose_name='Market Type')),
                ('selling_price_case', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Selling Price (Case)')),
                ('open_market_pack_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ng_pack_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('small_supermarket_pack_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('gram_unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_pack', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gram_pack', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pack_case', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kd_case_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kd_unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kd_price_gram', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]