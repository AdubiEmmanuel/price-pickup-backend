from django.db import migrations


def populate_customers(apps, schema_editor):
    Customer = apps.get_model('stock', 'Customer')
    CustomerStockEntry = apps.get_model('stock', 'CustomerStockEntry')

    seen = {}
    counter = 0
    for entry in CustomerStockEntry.objects.all():
        key = (entry.customer_name, entry.location)
        customer = seen.get(key)
        if customer is None:
            counter += 1
            customer = Customer.objects.create(
                customer_code=f'AUTO-{counter:04d}',
                customer_name=entry.customer_name,
                location=entry.location,
            )
            seen[key] = customer
        entry.customer = customer
        entry.save(update_fields=['customer'])


def noop_reverse(apps, schema_editor):
    # Data migration is one-way; reversing would need to reconstruct the
    # free-text fields, which is unnecessary for this app's history.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0003_customer'),
    ]

    operations = [
        migrations.RunPython(populate_customers, noop_reverse),
    ]
