from django.conf.urls import url
from scrapesites import views

urlpatterns = [
    url(r'^$', views.url_search_results, name='url_search_result'),
    url(r'logs', views.logs, name='logs'),
    url(r'scan', views.scan, name='scan'),
]
