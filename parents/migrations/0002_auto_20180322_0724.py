# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-22 07:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parent',
            name='create_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Create date'),
        ),
        migrations.AlterField(
            model_name='parent',
            name='modified_date',
            field=models.DateField(default=django.utils.timezone.now, null=True, verbose_name='Modified date'),
        ),
    ]
