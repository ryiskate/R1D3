from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.EducationDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.EducationDashboardView.as_view(), name='dashboard'),
    path('classes/', views.ClassesView.as_view(), name='classes'),
    path('materials/', views.CourseMaterialsView.as_view(), name='materials'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('tasks/', views.EducationTasksView.as_view(), name='tasks'),
    path('tasks/batch-update/', views.EducationTaskBatchUpdateView.as_view(), name='batch_task_update'),
]
