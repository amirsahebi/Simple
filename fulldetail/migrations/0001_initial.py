# Generated by Django 3.2.15 on 2022-09-03 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_open', models.BooleanField(default=False)),
                ('count', models.IntegerField()),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('percentage', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountaddress', models.CharField(blank=True, default='', max_length=200)),
                ('userid', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, default='', max_length=200)),
                ('bio', models.CharField(blank=True, default='', max_length=200)),
                ('loc', models.CharField(blank=True, default='', max_length=200)),
                ('joined', models.CharField(blank=True, default='', max_length=200)),
                ('followers', models.IntegerField(blank=True, null=True)),
                ('following', models.IntegerField(blank=True, null=True)),
                ('tweet_num', models.IntegerField(blank=True, null=True)),
                ('profile_image_url', models.CharField(blank=True, default='', max_length=200)),
                ('processfield', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fulldetail.process')),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, default='', max_length=10000)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fulldetail.profile')),
            ],
        ),
    ]
