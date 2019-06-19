# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-13 07:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0022_classdefinition_event_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classdefinition',
            name='event_title',
        ),
        migrations.RemoveField(
            model_name='classdefinition',
            name='gc_event_id',
        ),
        migrations.AddField(
            model_name='classrollout',
            name='gc_event_id',
            field=models.CharField(max_length=200, null=True, verbose_name='Google Calendar Event Id'),
        ),
        migrations.AddField(
            model_name='classrollout',
            name='gc_event_title',
            field=models.CharField(default=1, max_length=500, verbose_name='Google Calendar Event Title'),
            preserve_default=False,
        ),
    ]