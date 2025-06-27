from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # R1D3 Tasks URLs
    path('R1D3-tasks/', views.GlobalTaskDashboardView.as_view(), name='global_task_dashboard'),
    path('R1D3-tasks/newtask/', views.R1D3TaskCreateView.as_view(), name='r1d3_task_create'),
    path('test/', views.TestView.as_view(), name='test'),
]
