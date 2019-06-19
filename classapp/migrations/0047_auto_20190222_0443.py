# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-02-22 04:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0046_auto_20190222_0313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='gd_link',
        ),
        migrations.AddField(
            model_name='book',
            name='answer_key',
            field=models.CharField(max_length=512, null=True, verbose_name='Answer link'),
        ),
    ]
