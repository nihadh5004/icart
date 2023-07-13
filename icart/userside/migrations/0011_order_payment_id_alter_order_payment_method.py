# Generated by Django 4.2.2 on 2023-07-08 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0010_alter_order_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('PREPAID', 'Prepaid'), ('COD', 'Cash on Delivery')], max_length=20),
        ),
    ]
