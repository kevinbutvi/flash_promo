# Generated by Django 5.1.7 on 2025-03-23 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='regular_prince',
            new_name='regular_price',
        ),
    ]
