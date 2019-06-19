# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-13 10:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('parents', '0001_initial'),
        ('beaconapp', '0001_initial'),
        ('staff', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='upgradeform',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upgrade_parent', to='parents.Parent'),
        ),
        migrations.AddField(
            model_name='upgradeform',
            name='staff',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upgrade_staff', to='staff.Staff'),
        ),
        migrations.AddField(
            model_name='upgradeform',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upgrade_student', to='students.Student'),
        ),
        migrations.AddField(
            model_name='upgradeform',
            name='duration',
            field=models.CharField(max_length=200, verbose_name='Duration', default='1 Hour'),
        ),
        migrations.AddField(
            model_name='discontinuationform',
            name='reason',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='discontinuationform',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discontinuation_parent', to='parents.Parent'),
        ),
        migrations.AddField(
            model_name='discontinuationform',
            name='staff',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discontinuation_staff', to='staff.Staff'),
        ),
        migrations.AddField(
            model_name='discontinuationform',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discontinuation_student', to='students.Student'),
        ),
        migrations.AddField(
            model_name='breaktime',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='break_parent', to='parents.Parent'),
        ),
        migrations.AddField(
            model_name='breaktime',
            name='reason',
            field=models.TextField(null=True),
        ),
    ]