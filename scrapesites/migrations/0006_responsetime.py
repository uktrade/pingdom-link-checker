# Generated by Django 2.0.5 on 2018-05-25 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapesites', '0005_auto_20180523_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Responsetime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_time', models.TimeField()),
            ],
        ),
    ]