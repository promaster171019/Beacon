# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-12 08:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0027_staff_locations'),
        ('classapp', '0039_lessonplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='classrollout',
            name='weekly_report_changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='weekly_report_changed', to='staff.Staff'),
        ),
        migrations.AddField(
            model_name='classrollout',
            name='weekly_report_created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='weekly_report_created', to='staff.Staff'),
        ),
        migrations.AddField(
            model_name='classrollout',
            name='weekly_report_date',
            field=models.DateTimeField(null=True),
        ),
    ]
