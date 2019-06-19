# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-09 11:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0016_auto_20180604_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentinclass',
            name='class_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='classapp.ClassRollout'),
        ),
    ]
