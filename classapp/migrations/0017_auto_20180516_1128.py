# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-16 11:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0016_auto_20180516_0444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classdefinition',
            name='end_date',
            field=models.DateTimeField(verbose_name='End class date'),
        ),
        migrations.AlterField(
            model_name='classdefinition',
            name='start_date',
            field=models.DateTimeField(verbose_name='Start class date'),
        ),
    ]
