import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_alter_customerstockentry_brand'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=50, unique=True, verbose_name='Customer Code')),
                ('customer_name', models.CharField(max_length=255, verbose_name='Customer Name')),
                ('location', models.CharField(max_length=255, verbose_name='Location')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['customer_name'],
            },
        ),
        migrations.AddField(
            model_name='customerstockentry',
            name='customer',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='stock_entries',
                to='stock.customer',
                verbose_name='Customer',
            ),
        ),
    ]
