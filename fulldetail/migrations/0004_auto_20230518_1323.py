# Generated by Django 3.2.18 on 2023-05-18 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fulldetail', '0003_auto_20221116_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='since',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='process',
            name='until',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='created_at',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
