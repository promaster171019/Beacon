# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-23 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parents', '0002_auto_20180322_0724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parent',
            name='photo',
            field=models.TextField(blank=True, null=True, verbose_name='Photo'),
        ),
    ]
