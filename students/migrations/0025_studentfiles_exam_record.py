# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-23 05:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0024_student_subjects'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentfiles',
            name='exam_record',
            field=models.BooleanField(default=False),
        ),
    ]
