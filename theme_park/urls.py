from django.urls import path
from . import views

app_name = 'theme_park'

urlpatterns = [
    path('', views.ThemeParkDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.ThemeParkDashboardView.as_view(), name='dashboard'),
    path('projects/', views.ParkProjectsView.as_view(), name='projects'),
    path('attractions/', views.AttractionsView.as_view(), name='attractions'),
    path('map/', views.ParkMapView.as_view(), name='map'),
    path('tasks/', views.ThemeParkTasksView.as_view(), name='tasks'),
    path('tasks/create/', views.ThemeParkTaskCreateView.as_view(), name='task_create'),
    path('tasks/newtask/', views.ThemeParkTaskCreateView.as_view(), name='newtask'),
    path('tasks/<int:pk>/', views.ThemeParkTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.ThemeParkTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.ThemeParkTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/status-update/', views.ThemeParkTaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/hours-update/', views.ThemeParkTaskHoursUpdateView.as_view(), name='task_hours_update'),
    path('tasks/batch-update/', views.ThemeParkTaskBatchUpdateView.as_view(), name='task_batch_update'),
]
