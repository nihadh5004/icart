# Generated by Django 4.2.2 on 2023-07-13 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartside', '0006_alter_wallet_money'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='money',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]