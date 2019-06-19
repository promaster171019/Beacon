# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-07-27 07:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0020_studentmakeup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentmakeup',
            name='cancelled_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='makeup_cancelled', to='students.StudentInClass', verbose_name='Cancelled class'),
        ),
        migrations.AlterField(
            model_name='studentmakeup',
            name='makeup_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='makeup_new', to='students.StudentInClass', verbose_name='Makeup class'),
        ),
    ]