# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-22 02:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0027_staff_locations'),
        ('classapp', '0031_auto_20180628_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='material',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='material_created_by', to='staff.Staff'),
        ),
    ]
