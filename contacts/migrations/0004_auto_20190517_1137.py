# Generated by Django 2.1 on 2019-05-17 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_auto_20190517_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='time',
            field=models.TimeField(default='11:37', verbose_name='Time'),
        ),
    ]