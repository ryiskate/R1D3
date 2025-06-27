from django.urls import path
from . import views
from . import game_views, game_task_views, education_task_views, social_media_task_views, arcade_task_views, theme_park_task_views, r1d3_task_views, test_views, unified_r1d3_task_forms
# Import the unified task views
from . import unified_task_views
# Import the unified task forms
from . import unified_task_forms
# Import the all tasks views
from . import all_tasks_views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectDashboardView.as_view(), name='dashboard'),
    path('list/', views.ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('<int:project_id>/tasks/', views.TaskListView.as_view(), name='project_tasks'),
    
    # Social Media Task URLs
    path('social-media/tasks/', unified_task_views.SocialMediaTaskDashboardView.as_view(), name='social_media_task_dashboard'),
    path('social-media/tasks/create/', unified_task_forms.SocialMediaTaskCreateView.as_view(), name='social_media_task_create'),
    path('social-media/tasks/<int:pk>/', social_media_task_views.SocialMediaTaskDetailView.as_view(), name='social_media_task_detail'),
    path('social-media/tasks/<int:pk>/update/', unified_task_forms.SocialMediaTaskUpdateView.as_view(), name='social_media_task_update'),
    path('social-media/tasks/<int:pk>/delete/', social_media_task_views.SocialMediaTaskDeleteView.as_view(), name='social_media_task_delete'),
    path('social-media/tasks/batch-update/', social_media_task_views.SocialMediaTaskBatchUpdateView.as_view(), name='social_media_task_batch_update'),
    path('social-media/tasks/status-update/', social_media_task_views.SocialMediaTaskStatusUpdateView.as_view(), name='social_media_task_status_update'),
    path('social-media/tasks/hours-update/', social_media_task_views.SocialMediaTaskHoursUpdateView.as_view(), name='social_media_task_hours_update'),
    
    # Arcade Task URLs
    path('arcade/tasks/', unified_task_views.ArcadeTaskDashboardView.as_view(), name='arcade_task_dashboard'),
    path('arcade/tasks/create/', unified_task_forms.ArcadeTaskCreateView.as_view(), name='arcade_task_create'),
    path('arcade/tasks/<int:pk>/', arcade_task_views.ArcadeTaskDetailView.as_view(), name='arcade_task_detail'),
    path('arcade/tasks/<int:pk>/update/', unified_task_forms.ArcadeTaskUpdateView.as_view(), name='arcade_task_update'),
    path('arcade/tasks/<int:pk>/delete/', arcade_task_views.ArcadeTaskDeleteView.as_view(), name='arcade_task_delete'),
    path('arcade/tasks/batch-update/', arcade_task_views.ArcadeTaskBatchUpdateView.as_view(), name='arcade_task_batch_update'),
    path('arcade/tasks/status-update/', arcade_task_views.ArcadeTaskStatusUpdateView.as_view(), name='arcade_task_status_update'),
    path('arcade/tasks/hours-update/', arcade_task_views.ArcadeTaskHoursUpdateView.as_view(), name='arcade_task_hours_update'),
    
    # Theme Park Task URLs
    path('theme-park/tasks/', unified_task_views.ThemeParkTaskDashboardView.as_view(), name='theme_park_task_dashboard'),
    path('theme-park/tasks/create/', unified_task_forms.ThemeParkTaskCreateView.as_view(), name='theme_park_task_create'),
    path('theme-park/tasks/<int:pk>/', theme_park_task_views.ThemeParkTaskDetailView.as_view(), name='theme_park_task_detail'),
    path('theme-park/tasks/<int:pk>/update/', unified_task_forms.ThemeParkTaskUpdateView.as_view(), name='theme_park_task_update'),
    path('theme-park/tasks/<int:pk>/delete/', theme_park_task_views.ThemeParkTaskDeleteView.as_view(), name='theme_park_task_delete'),
    path('theme-park/tasks/batch-update/', theme_park_task_views.ThemeParkTaskBatchUpdateView.as_view(), name='theme_park_task_batch_update'),
    path('theme-park/tasks/status-update/', theme_park_task_views.ThemeParkTaskStatusUpdateView.as_view(), name='theme_park_task_status_update'),
    path('theme-park/tasks/hours-update/', theme_park_task_views.ThemeParkTaskHoursUpdateView.as_view(), name='theme_park_task_hours_update'),
    
    # General R1D3 Task URLs
    path('r1d3/tasks/', unified_task_views.R1D3TaskDashboardView.as_view(), name='r1d3_task_dashboard'),
    path('r1d3/tasks/create/', unified_task_forms.R1D3TaskCreateView.as_view(), name='r1d3_task_create'),
    path('r1d3/tasks/<int:pk>/', r1d3_task_views.R1D3TaskDetailView.as_view(), name='r1d3_task_detail'),
    path('r1d3/tasks/<int:pk>/update/', unified_task_forms.R1D3TaskUpdateView.as_view(), name='r1d3_task_update'),
    path('r1d3/tasks/<int:pk>/delete/', r1d3_task_views.R1D3TaskDeleteView.as_view(), name='r1d3_task_delete'),
    path('r1d3/tasks/batch-update/', r1d3_task_views.R1D3TaskBatchUpdateView.as_view(), name='r1d3_task_batch_update'),
    path('r1d3/tasks/status-update/', r1d3_task_views.R1D3TaskStatusUpdateView.as_view(), name='r1d3_task_status_update'),
    path('r1d3/tasks/hours-update/', r1d3_task_views.R1D3TaskHoursUpdateView.as_view(), name='r1d3_task_hours_update'),
    
    # Game Development Task URLs
    path('game/tasks/', unified_task_views.GameTaskDashboardView.as_view(), name='game_task_dashboard'),
    path('game/tasks/create/', unified_task_forms.GameTaskCreateView.as_view(), name='game_task_create'),
    path('game/tasks/<int:pk>/', game_views.GameTaskDetailView.as_view(), name='game_task_detail'),
    path('game/tasks/<int:pk>/update/', unified_task_forms.GameTaskUpdateView.as_view(), name='game_task_update'),
    path('game/tasks/<int:pk>/delete/', game_views.GameTaskDeleteView.as_view(), name='game_task_delete'),
    path('game/tasks/batch-update/', game_task_views.GameTaskBatchUpdateView.as_view(), name='game_task_batch_update'),
    path('game/tasks/status-update/', game_task_views.GameTaskStatusUpdateView.as_view(), name='game_task_status_update'),
    path('game/tasks/hours-update/', game_task_views.GameTaskHoursUpdateView.as_view(), name='game_task_hours_update'),
    path('game/tasks/kanban/', game_views.GameTaskKanbanView.as_view(), name='game_task_kanban'),
    
    # Education Task URLs
    path('education/tasks/', unified_task_views.EducationTaskDashboardView.as_view(), name='education_task_dashboard'),
    path('education/tasks/create/', unified_task_forms.EducationTaskCreateView.as_view(), name='education_task_create'),
    path('education/tasks/<int:pk>/', education_task_views.EducationTaskDetailView.as_view(), name='education_task_detail'),
    path('education/tasks/<int:pk>/update/', unified_task_forms.EducationTaskUpdateView.as_view(), name='education_task_update'),
    path('education/tasks/<int:pk>/delete/', education_task_views.EducationTaskDeleteView.as_view(), name='education_task_delete'),
    path('education/tasks/batch-update/', education_task_views.EducationTaskBatchUpdateView.as_view(), name='education_task_batch_update'),
    path('education/tasks/status-update/', education_task_views.EducationTaskStatusUpdateView.as_view(), name='education_task_status_update'),
    path('education/tasks/hours-update/', education_task_views.EducationTaskHoursUpdateView.as_view(), name='education_task_hours_update'),
    
    # All Tasks URLs have been removed - now using core:global_task_dashboard instead
    
    # Test views
    path('test-r1d3-button/', test_views.TestR1D3ButtonView.as_view(), name='test_r1d3_button'),
    path('debug-button/', test_views.DebugButtonView.as_view(), name='debug_button'),
    path('test-education-form/', test_views.TestEducationTaskFormView.as_view(), name='test_education_form'),
]
