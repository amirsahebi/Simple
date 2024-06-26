# Generated by Django 3.2.15 on 2022-08-30 11:57

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
                ('created_at', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountaddress', models.CharField(blank=True, default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.profile')),
                ('processfield', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.process')),
            ],
        ),
        migrations.AddField(
            model_name='process',
            name='starting_node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.profile'),
        ),
    ]
