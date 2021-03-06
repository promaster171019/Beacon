# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-15 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0023_auto_20180613_0716'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='parent_calendarId',
            field=models.CharField(max_length=400, null=True, verbose_name='Parent Google Calendar ID'),
        ),
        migrations.AlterField(
            model_name='location',
            name='calendarId',
            field=models.CharField(max_length=400, null=True, verbose_name='Google Calendar ID'),
        ),
    ]
