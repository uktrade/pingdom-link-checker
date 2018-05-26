from django.contrib import admin

from .models import Url_status, Urllist, Responsetime
# # Register your models here.

@admin.register(Url_status)
class url_status_admin(admin.ModelAdmin):
	list_display = ('site', 'source_url', 'broken_url')

@admin.register(Urllist)
class url_list_admin(admin.ModelAdmin):
	list_display = ('url', 'team', 'enable', 'bad_link','slack_sent')

@admin.register(Responsetime)
class response_time_admin(admin.ModelAdmin):
	list_display = ('id', 'response_time', 'previous_check_state')
