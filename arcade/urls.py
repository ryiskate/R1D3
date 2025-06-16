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
]
