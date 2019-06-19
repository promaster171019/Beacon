# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-26 07:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0027_classrolloutlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='classrollout',
            name='duration',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='class_rollout', to='classapp.ClassDuration'),
            preserve_default=False,
        ),
    ]
