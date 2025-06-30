from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'social_media'

urlpatterns = [
    path('', views.SocialMediaDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.SocialMediaDashboardView.as_view(), name='dashboard'),
    path('schedule/', views.PostScheduleView.as_view(), name='schedule'),
    path('ideas/', views.PostIdeasView.as_view(), name='ideas'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('tasks/', views.SocialMediaTasksView.as_view(), name='tasks'),
    # Direct link to the task creation form
    path('tasks/create/', views.SocialMediaTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.SocialMediaTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.SocialMediaTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.SocialMediaTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/batch-update/', views.SocialMediaTaskBatchUpdateView.as_view(), name='batch_task_update'),
    path('tasks/<int:pk>/status-update/', views.SocialMediaTaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/hours-update/', views.SocialMediaTaskHoursUpdateView.as_view(), name='task_hours_update'),
]
