# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-10 02:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0049_auto_20190508_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstory',
            name='justificacion',
            field=models.TextField(default='', help_text='justifique por qué se va a cancelar el user story', max_length=500, null=True, verbose_name='justificación'),
        ),
    ]