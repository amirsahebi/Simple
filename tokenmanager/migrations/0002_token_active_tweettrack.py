# Generated by Django 3.2.16 on 2022-11-15 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokenmanager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='active_tweettrack',
            field=models.BooleanField(default=False),
        ),
    ]
