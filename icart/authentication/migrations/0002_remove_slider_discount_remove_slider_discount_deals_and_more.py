# Generated by Django 4.2.2 on 2023-07-15 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productside', '0005_productvariant_discount'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slider',
            name='Discount',
        ),
        migrations.RemoveField(
            model_name='slider',
            name='Discount_deals',
        ),
        migrations.RemoveField(
            model_name='slider',
            name='Links',
        ),
        migrations.RemoveField(
            model_name='slider',
            name='Product_name',
        ),
        migrations.RemoveField(
            model_name='slider',
            name='Sale',
        ),
        migrations.AddField(
            model_name='slider',
            name='Product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='productside.productvariant'),
        ),
    ]