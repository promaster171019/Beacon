# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-23 12:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20180322_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='photo',
            field=models.TextField(blank=True, null=True, verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='token',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 23, 13, 18, 3, 471385)),
        ),
    ]
