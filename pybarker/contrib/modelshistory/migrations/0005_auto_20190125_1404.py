# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-25 09:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modelshistory', '0004_auto_20180713_1111'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historymodelentry',
            options={'ordering': ('-id',), 'verbose_name': 'log entry', 'verbose_name_plural': 'log entries'},
        ),
    ]
