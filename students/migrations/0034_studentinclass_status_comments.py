# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-25 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0033_studentmakeup_original_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinclass',
            name='status_comments',
            field=models.TextField(max_length=200, null=True),
        ),
    ]
