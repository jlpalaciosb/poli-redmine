# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-07 02:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0045_auto_20190506_1535'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fase',
            options={'default_permissions': (), 'ordering': ['orden']},
        ),
        migrations.AddField(
            model_name='sprint',
            name='fecha_fin',
            field=models.DateField(help_text='La fecha en la que finaliza un sprint', null=True, verbose_name='fecha de finalizacion'),
        ),
    ]
