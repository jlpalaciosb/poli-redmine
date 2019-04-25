# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-23 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0029_auto_20190421_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='campopersonalizado',
            name='nombre_campo',
            field=models.CharField(max_length=20, verbose_name='Nombre del campo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='campopersonalizado',
            name='tipo_dato',
            field=models.CharField(choices=[('NUMERO', 'Numero'), ('STRING', 'String')], default='STRING', max_length=7, verbose_name='Tipo de dato del Campo'),
        ),
        migrations.RemoveField(
            model_name='campopersonalizado',
            name='estado',
        ),
        migrations.RemoveField(
            model_name='campopersonalizado',
            name='tipoDeDato',
        ),
        migrations.AlterUniqueTogether(
            name='campopersonalizado',
            unique_together=set([('tipoUS', 'nombre_campo')]),
        ),
        migrations.AlterUniqueTogether(
            name='tipous',
            unique_together=set([('nombre', 'proyecto')]),
        ),
    ]
