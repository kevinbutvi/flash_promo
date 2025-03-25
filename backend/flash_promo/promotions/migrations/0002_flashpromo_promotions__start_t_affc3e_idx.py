# Generated by Django 5.1.7 on 2025-03-23 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
        ('promotions', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='flashpromo',
            index=models.Index(fields=['start_time', 'end_time', 'is_active'], name='promotions__start_t_affc3e_idx'),
        ),
    ]
