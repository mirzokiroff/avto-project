# Generated by Django 5.2.3 on 2025-07-21 20:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_entry_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='exitlog',
            name='area',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.PROTECT, to='apps.area'),
            preserve_default=False,
        ),
    ]
