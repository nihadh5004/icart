# Generated by Django 4.2.2 on 2023-07-01 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cartside', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercart',
            old_name='user_id',
            new_name='user',
        ),
    ]
