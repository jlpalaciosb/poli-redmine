# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-03-28 01:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0005_merge_20190325_2306'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolproyecto',
            name='nombre',
            field=models.CharField(default='Scrum Master', max_length=20, verbose_name='Nombre'),
            preserve_default=False,
        ),
    ]
