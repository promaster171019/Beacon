# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-28 12:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_auto_20180327_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 28, 13, 59, 43, 720363)),
        ),
    ]
