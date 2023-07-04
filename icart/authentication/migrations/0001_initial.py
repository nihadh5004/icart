# Generated by Django 4.2.2 on 2023-06-30 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Image', models.ImageField(upload_to='media/slider_imgs')),
                ('Discount_deals', models.CharField(choices=[('HOT DEALS', 'HOT DEALS'), ('NEW ARRIVALS', 'NEW ARRIVALS')], max_length=100)),
                ('Sale', models.IntegerField()),
                ('Product_name', models.CharField(max_length=200)),
                ('Discount', models.IntegerField()),
                ('Links', models.CharField(max_length=200)),
            ],
        ),
    ]
