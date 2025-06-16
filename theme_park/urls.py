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
]
