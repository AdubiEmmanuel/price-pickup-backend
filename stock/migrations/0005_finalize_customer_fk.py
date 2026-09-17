import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_populate_customer_data'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='customerstockentry',
            name='stock_custo_custome_b04451_idx',
        ),
        migrations.AlterField(
            model_name='customerstockentry',
            name='customer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='stock_entries',
                to='stock.customer',
                verbose_name='Customer',
            ),
        ),
        migrations.RemoveField(
            model_name='customerstockentry',
            name='customer_name',
        ),
        migrations.RemoveField(
            model_name='customerstockentry',
            name='location',
        ),
        migrations.AddIndex(
            model_name='customerstockentry',
            index=models.Index(fields=['customer'], name='stock_custo_custome_6ebdb7_idx'),
        ),
    ]
