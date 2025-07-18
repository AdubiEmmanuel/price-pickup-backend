# Generated by Django 4.2.7 on 2025-06-03 12:11

from django.db import migrations


def update_category_names(apps, schema_editor):
    """
    Update existing category names to match frontend requirements:
    - ORALS -> ORAL CARE
    """
    CompetitorPrice = apps.get_model('competitors', 'CompetitorPrice')

    # Update ORALS to ORAL CARE
    CompetitorPrice.objects.filter(sku_category='ORALS').update(sku_category='ORAL CARE')

    print("Updated category names: ORALS -> ORAL CARE")


def reverse_category_names(apps, schema_editor):
    """
    Reverse the category name changes
    """
    CompetitorPrice = apps.get_model('competitors', 'CompetitorPrice')

    # Reverse ORAL CARE to ORALS
    CompetitorPrice.objects.filter(sku_category='ORAL CARE').update(sku_category='ORALS')

    print("Reversed category names: ORAL CARE -> ORALS")


class Migration(migrations.Migration):

    dependencies = [
        ('competitors', '0005_remove_competitorprice_market_type_and_more'),
    ]

    operations = [
        migrations.RunPython(update_category_names, reverse_category_names),
    ]
