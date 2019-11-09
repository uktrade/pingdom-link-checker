from django.db import models

# Create your models here.


class Urllist(models.Model):
    site_url = models.URLField()
    team = models.CharField(max_length=60)
    # slack_url = models.URLField()
    enable = models.BooleanField(default=True)
    broken_link_found = models.BooleanField(default=False)
    slack_sent = models.BooleanField(default=False)
    ignore_prefix = models.TextField(default='')

    def __str__(self):
        return self.site_url


class Brokenlink(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    site_url = models.URLField()
    source_url = models.URLField()
    broken_link = models.TextField()
    temp_url = models.ForeignKey(Urllist, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('site_url', 'source_url', 'broken_link')


class Responsetime(models.Model):
    response_time = models.FloatField(default=0.00)
    previous_check_state = models.BooleanField(default=True)
