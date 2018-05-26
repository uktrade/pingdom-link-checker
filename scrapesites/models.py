from django.db import models

# Create your models here.

class Url_status(models.Model):
    site = models.TextField(primary_key=True)
    source_url = models.TextField()
    broken_url = models.TextField()
    class Meta:
        db_table = 'url_status'
        unique_together = ('site', 'source_url', 'broken_url')

class Urllist(models.Model):
    url = models.URLField()
    team = models.CharField(max_length=60)
    enable = models.BooleanField(default=True)
    bad_link = models.BooleanField(default=False)
    slack_sent = models.BooleanField(default=False)

class Responsetime(models.Model):
    response_time = models.FloatField(default=0.00)
    previous_check_state = models.BooleanField(default=True)
