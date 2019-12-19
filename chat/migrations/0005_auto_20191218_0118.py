# Generated by Django 2.2.6 on 2019-12-17 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20191217_2006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatroom',
            old_name='rooms',
            new_name='last_message',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='slot',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='last_message',
        ),
        migrations.AddField(
            model_name='chatroom',
            name='name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='message',
            name='time',
            field=models.CharField(default='01:18', max_length=10),
        ),
    ]
