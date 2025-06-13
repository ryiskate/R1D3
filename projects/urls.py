from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectDashboardView.as_view(), name='dashboard'),
    path('list/', views.ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('<int:project_id>/tasks/', views.TaskListView.as_view(), name='project_tasks'),
]
