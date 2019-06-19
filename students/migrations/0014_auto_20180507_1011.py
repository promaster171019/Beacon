# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-07 10:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0013_auto_20180330_0823'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='review',
            new_name='review_received',
        ),
        migrations.AddField(
            model_name='student',
            name='allergy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='review_text',
            field=models.TextField(blank=True, null=True, verbose_name='Review Text'),
        ),
        migrations.AddField(
            model_name='student',
            name='type_allergy',
            field=models.TextField(blank=True, null=True, verbose_name='Type of Allergy'),
        ),
    ]
