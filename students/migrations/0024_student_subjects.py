# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-13 08:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0031_auto_20180628_0933'),
        ('students', '0023_studentinclasslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='subjects',
            field=models.ManyToManyField(null=True, related_name='students', to='classapp.Subject'),
        ),
    ]
