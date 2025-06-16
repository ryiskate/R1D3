from django.urls import path
from . import views

app_name = 'social_media'

urlpatterns = [
    path('', views.SocialMediaDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.SocialMediaDashboardView.as_view(), name='dashboard'),
    path('schedule/', views.PostScheduleView.as_view(), name='schedule'),
    path('ideas/', views.PostIdeasView.as_view(), name='ideas'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('tasks/', views.SocialMediaTasksView.as_view(), name='tasks'),
]
