# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-16 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0025_auto_20190416_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='flujo',
            name='cantidadFases',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='flujo',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='flujo',
            unique_together=set([('proyecto', 'nombre')]),
        ),
    ]