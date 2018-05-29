from django.db import models

# Create your models here.

class Brokenlink(models.Model):
    site_url = models.URLField()
    source_url = models.URLField()
    broken_link = models.TextField()
    class Meta:
        unique_together = ('site_url', 'source_url', 'broken_link')

class Urllist(models.Model):
    site_url = models.URLField()
    team = models.CharField(max_length=60)
    enable = models.BooleanField(default=True)
    broken_link_found = models.BooleanField(default=False)
    slack_sent = models.BooleanField(default=False)
    ignore_prefix = models.TextField(default='')

class Responsetime(models.Model):
    response_time = models.FloatField(default=0.00)
    previous_check_state = models.BooleanField(default=True)
