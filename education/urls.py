from django.urls import path
from . import views
from . import debug_views

app_name = 'education'

urlpatterns = [
    path('', views.EducationDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.EducationDashboardView.as_view(), name='dashboard'),
    path('classes/', views.ClassesView.as_view(), name='classes'),
    path('materials/', views.CourseMaterialsView.as_view(), name='materials'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('tasks/', views.EducationTasksView.as_view(), name='tasks'),  # Using the education app's view
    path('debug-tasks/', debug_views.DebugEducationTasksView.as_view(), name='debug_tasks'),
    path('tasks/newtask/', views.EducationTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.EducationTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.EducationTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.EducationTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/status-update/', views.EducationTaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/hours-update/', views.EducationTaskHoursUpdateView.as_view(), name='task_hours_update'),
    path('tasks/batch-update/', views.EducationTaskBatchUpdateView.as_view(), name='batch_task_update'),
]
