# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-23 19:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0030_auto_20190423_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campopersonalizado',
            name='campo',
        ),
    ]
