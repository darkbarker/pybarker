# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-07-12 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelshistory', '0002_auto_20180712_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='historymodelentry',
            name='tag',
            field=models.TextField(blank=True, null=True),
        ),
    ]
