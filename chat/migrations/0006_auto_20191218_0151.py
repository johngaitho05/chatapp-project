# Generated by Django 2.2.6 on 2019-12-17 22:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20191218_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='last_message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_last_message', to='chat.Message'),
        ),
        migrations.AlterField(
            model_name='message',
            name='time',
            field=models.CharField(default='01:51', max_length=10),
        ),
    ]