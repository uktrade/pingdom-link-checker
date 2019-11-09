from django.contrib import admin

from .models import Brokenlink, Urllist, Responsetime
# # Register your models here.


@admin.register(Brokenlink)
class broken_link_admin(admin.ModelAdmin):
    list_display = ('site_url', 'source_url', 'broken_link', 'created_at')

    # list_display = ('site_url', 'source_url', 'broken_link', 'created_at',
    #                 'display_team', 'broken_link_status')

    # def display_team(self, obj):
    #     return obj.temp_url.team,

    # def broken_link_status(self, obj):
    #     return obj.temp_url.broken_link_found


@admin.register(Urllist)
class url_list_admin(admin.ModelAdmin):
    list_display = ('site_url', 'team', 'enable',
                    'broken_link_found', 'slack_sent', 'ignore_prefix')


@admin.register(Responsetime)
class response_time_admin(admin.ModelAdmin):
    list_display = ('id', 'response_time', 'previous_check_state')
