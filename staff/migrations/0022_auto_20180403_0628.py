# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-03 06:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0021_auto_20180330_0827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 3, 7, 28, 12, 367016)),
        ),
    ]