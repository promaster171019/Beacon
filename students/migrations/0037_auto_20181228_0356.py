# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-28 03:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0036_auto_20181226_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinclass',
            name='c_manager_note',
            field=models.TextField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='manager_note',
            field=models.TextField(max_length=200, null=True),
        ),
    ]