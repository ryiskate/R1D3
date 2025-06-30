from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # R1D3 Tasks URLs
    path('R1D3-tasks/', views.GlobalTaskDashboardView.as_view(), name='global_task_dashboard'),
    path('R1D3-tasks/newtask/', views.R1D3TaskCreateView.as_view(), name='r1d3_task_create'),
    # Updated URLs with task_type parameter
    path('R1D3-tasks/<str:task_type>/<int:pk>/', views.R1D3TaskDetailView.as_view(), name='r1d3_task_detail'),
    path('R1D3-tasks/<str:task_type>/<int:pk>/update/', views.R1D3TaskUpdateView.as_view(), name='r1d3_task_update'),
    path('R1D3-tasks/<str:task_type>/<int:pk>/delete/', views.R1D3TaskDeleteView.as_view(), name='r1d3_task_delete'),
    # Legacy URLs for backward compatibility
    path('R1D3-tasks/<int:pk>/', views.R1D3TaskDetailLegacyView.as_view(), name='r1d3_task_detail_legacy'),
    path('R1D3-tasks/<int:pk>/update/', views.R1D3TaskUpdateLegacyView.as_view(), name='r1d3_task_update_legacy'),
    path('R1D3-tasks/<int:pk>/delete/', views.R1D3TaskDeleteLegacyView.as_view(), name='r1d3_task_delete_legacy'),
    path('test/', views.TestView.as_view(), name='test'),
]
