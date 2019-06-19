# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-22 07:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0002_auto_20180313_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booksgiven',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created date'),
        ),
        migrations.AlterField(
            model_name='booksgiven',
            name='modified_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created date'),
        ),
        migrations.AlterField(
            model_name='classrollout',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='classrollout',
            name='modified_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='vacation',
            name='create_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Created date'),
        ),
    ]