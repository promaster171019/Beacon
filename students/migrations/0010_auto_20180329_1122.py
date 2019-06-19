# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-29 11:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_auto_20180329_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=200, verbose_name='Status')),
            ],
        ),
        migrations.RemoveField(
            model_name='student',
            name='active',
        ),
    ]
