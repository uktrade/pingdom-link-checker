from django.urls import path
from scrapesites import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('logs/', views.LogsView.as_view(), name='logs'),
    path('gecko/', views.GeckoBoard.as_view(), name='geckoReport'),
    path('gecko/broken_links_count/', views.GeckoBrokenLinkCount.as_view(), name='broken_links_count')
]
