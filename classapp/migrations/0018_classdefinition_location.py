# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-17 04:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0017_auto_20180516_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='classdefinition',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='classapp.Location'),
            preserve_default=False,
        ),
    ]
