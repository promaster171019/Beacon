# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-22 04:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0032_auto_20180822_0256'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='color',
            field=models.CharField(max_length=32, null=True, verbose_name='Room color'),
        ),
    ]
