# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-29 09:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_studentheardfrom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='review_date',
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
    ]
