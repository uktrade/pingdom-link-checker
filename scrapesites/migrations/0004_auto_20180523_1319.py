# Generated by Django 2.0.5 on 2018-05-23 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapesites', '0003_urllist_enable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urllist',
            name='team',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='urllist',
            name='url',
            field=models.URLField(),
        ),
    ]
