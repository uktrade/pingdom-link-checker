# Generated by Django 2.2.6 on 2019-10-30 16:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scrapesites', '0004_remove_urllist_slack_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='brokenlink',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brokenlink',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
