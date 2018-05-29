from django.contrib import admin

from .models import Brokenlink, Urllist, Responsetime
# # Register your models here.

@admin.register(Brokenlink)
class broken_link_admin(admin.ModelAdmin):
	list_display = ('site_url', 'source_url', 'broken_link')

@admin.register(Urllist)
class url_list_admin(admin.ModelAdmin):
	list_display = ('site_url', 'team', 'enable', 'broken_link_found', 'slack_sent', 'ignore_prefix')

@admin.register(Responsetime)
class response_time_admin(admin.ModelAdmin):
	list_display = ('id', 'response_time', 'previous_check_state')
