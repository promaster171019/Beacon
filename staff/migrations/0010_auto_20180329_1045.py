# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-29 10:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_auto_20180329_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 29, 11, 45, 1, 261834)),
        ),
    ]
