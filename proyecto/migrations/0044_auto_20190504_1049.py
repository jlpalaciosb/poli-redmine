# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-04 14:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0043_auto_20190504_0856'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fase',
            options={'default_permissions': (), 'ordering': ['orden']},
        ),
    ]