from django.contrib import admin

from .models import Url_status, Urllist
# # Register your models here.

@admin.register(Url_status)
class url_status_admin(admin.ModelAdmin):
	list_display = ('site', 'source_url', 'broken_url')

@admin.register(Urllist)
class url_list_admin(admin.ModelAdmin):
	list_display = ('url', 'team', 'enable')