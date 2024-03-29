# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-07-11 16:34

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.MODELSHISTORY_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryModelEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='action time')),
                ('object_id', models.TextField(blank=True, null=True, verbose_name='object id')),
                ('object_repr', models.CharField(max_length=200, verbose_name='object repr')),
                ('action_flag', models.PositiveSmallIntegerField(verbose_name='action flag')),
                ('field', models.CharField(blank=True, max_length=64, null=True, verbose_name='field name')),
                ('oldvalue', models.CharField(blank=True, max_length=512, null=True, verbose_name='old field value')),
                ('newvalue', models.CharField(blank=True, max_length=512, null=True, verbose_name='new field value')),
                ('item_object_id', models.TextField(blank=True, null=True, verbose_name='item object id')),
                ('item_object_repr', models.CharField(blank=True, max_length=200, null=True, verbose_name='item object repr')),
                ('comment', models.CharField(blank=True, max_length=256, null=True, verbose_name='comment')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', verbose_name='content type')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.MODELSHISTORY_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('-action_time',),
                'verbose_name': 'log entry',
                'verbose_name_plural': 'log entries',
            },
        ),
    ]
