# Generated by Django 2.0.5 on 2018-05-25 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapesites', '0006_responsetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsetime',
            name='response_time',
            field=models.FloatField(),
        ),
    ]