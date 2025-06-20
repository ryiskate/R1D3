from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('all-tasks/', views.GlobalTaskDashboardView.as_view(), name='global_task_dashboard'),
    path('test/', views.TestView.as_view(), name='test'),
]
