# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-07 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0010_auto_20180507_1034'),
        ('staff', '0026_auto_20180507_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='locations',
            field=models.ManyToManyField(related_name='staff_locations', to='classapp.Location'),
        ),
    ]
