# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-29 09:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_auto_20180328_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 29, 10, 55, 29, 294737)),
        ),
    ]
