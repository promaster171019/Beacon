# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-27 07:24
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20180323_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 27, 8, 24, 29, 661984)),
        ),
    ]
