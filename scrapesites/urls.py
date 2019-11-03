from django.urls import path
from scrapesites import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('logs/',views.LogsView.as_view(), name='logs'),
    # url(r'^$', views.url_search_results, name='url_search_result'),
    # url(r'logs', views.logs, name='logs'),
    # url(r'scan', views.scan, name='scan'),
]
