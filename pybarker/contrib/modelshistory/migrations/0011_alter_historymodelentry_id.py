# Generated by Django 3.2.25 on 2025-02-17 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelshistory', '0010_auto_20230723_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historymodelentry',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
