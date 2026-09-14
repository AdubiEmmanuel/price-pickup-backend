from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerStockEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=255, verbose_name='Customer Name')),
                ('location', models.CharField(max_length=255, verbose_name='Location')),
                ('sku_category', models.CharField(blank=True, choices=[('NUTRITION', 'NUTRITION'), ('ORAL CARE', 'ORAL CARE'), ('DEODORANT', 'DEODORANT'), ('SKIN CARE', 'SKIN CARE'), ('SALVORY', 'SALVORY')], max_length=255, null=True, verbose_name='SKU Category')),
                ('sku_size', models.CharField(blank=True, choices=[('BULK PACK', 'BULK PACK'), ('MID PACK', 'MID PACK'), ('REGULAR PACK', 'REGULAR PACK'), ('SMALL PACK', 'SMALL PACK'), ('POWDERS', 'POWDERS')], max_length=255, null=True, verbose_name='SKU Size')),
                ('brand', models.CharField(blank=True, choices=[('PEARS', 'PEARS'), ('VASELINE', 'VASELINE'), ('CLOSE UP', 'CLOSE UP'), ('PEPSODENT', 'PEPSODENT'), ('KNORR', 'KNORR'), ('ROYCO', 'ROYCO'), ('REXONA', 'REXONA')], max_length=255, null=True, verbose_name='Brand')),
                ('sku_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='SKU Name')),
                ('current_stock', models.PositiveIntegerField(blank=True, null=True, verbose_name='Current Stock')),
                ('sales_in', models.PositiveIntegerField(blank=True, null=True, verbose_name='Sales In (Stock Received)')),
                ('is_unilever', models.BooleanField(default=False, verbose_name='Is Unilever Product')),
                ('source', models.CharField(choices=[('CSV', 'Imported from CSV'), ('FORM', 'Created from form')], default='FORM', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='customerstockentry',
            index=models.Index(fields=['customer_name', 'location'], name='stock_custo_custome_b04451_idx'),
        ),
        migrations.AddIndex(
            model_name='customerstockentry',
            index=models.Index(fields=['sku_category'], name='stock_custo_sku_cat_1cfe18_idx'),
        ),
    ]
