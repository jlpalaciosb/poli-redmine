# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-03-21 18:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0003_auto_20190321_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='miembroproyecto',
            name='roles',
            field=models.ManyToManyField(to='proyecto.RolProyecto'),
        ),
    ]
