# Generated by Django 4.2.2 on 2023-07-15 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_remove_slider_discount_remove_slider_discount_deals_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='slider',
            name='Discount_deals',
            field=models.CharField(choices=[('HOT DEALS', 'HOT DEALS'), ('NEW ARRIVALS', 'NEW ARRIVALS'), ('SPECIAL OFFERS', 'SPECIAL OFFERS')], max_length=100, null=True),
        ),
    ]
