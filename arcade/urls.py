from django.urls import path
from . import views

app_name = 'arcade'

urlpatterns = [
    path('', views.ArcadeDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.ArcadeDashboardView.as_view(), name='dashboard'),
    path('projects/', views.ArcadeProjectsView.as_view(), name='projects'),
    path('locations/', views.LocationsView.as_view(), name='locations'),
    path('revenue/', views.RevenueView.as_view(), name='revenue'),
    path('tasks/', views.ArcadeTasksView.as_view(), name='tasks'),
    path('tasks/create/', views.ArcadeTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.ArcadeTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.ArcadeTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.ArcadeTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/status-update/', views.ArcadeTaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/hours-update/', views.ArcadeTaskHoursUpdateView.as_view(), name='task_hours_update'),
    path('tasks/batch-update/', views.ArcadeTaskBatchUpdateView.as_view(), name='task_batch_update'),
]
