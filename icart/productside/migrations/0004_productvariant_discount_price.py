# Generated by Django 4.2.2 on 2023-07-15 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productside', '0003_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]