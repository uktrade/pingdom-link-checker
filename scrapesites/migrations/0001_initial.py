# Generated by Django 2.0.5 on 2018-05-26 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brokenlinks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_url', models.TextField()),
                ('source_url', models.TextField()),
                ('broken_link', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Responsetime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_time', models.FloatField(default=0.0)),
                ('previous_check_state', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Urllist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_url', models.URLField()),
                ('team', models.CharField(max_length=60)),
                ('enable', models.BooleanField(default=True)),
                ('broken_link_found', models.BooleanField(default=False)),
                ('slack_sent', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='brokenlinks',
            unique_together={('site_url', 'source_url', 'broken_link')},
        ),
    ]
