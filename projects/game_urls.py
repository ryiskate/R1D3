from django.urls import path
from django.shortcuts import redirect
from . import game_views
from .gdd_task_views import GDDTaskStatusUpdateView, BatchTaskUpdateView
from .game_task_views import GameTaskStatusUpdateView, GameTaskHoursUpdateView, GameTaskBatchUpdateView
from .game_task_dashboard_view import GameTaskDashboardView
from .gdd_views import (GameDesignDocumentEditView, TaskGDDSectionLinkView, GameDesignDocumentDeleteView)
from .gdd_feature_views import (ExtractFeaturesView, GDDFeaturesListView, ConvertFeatureToTaskView, 
                              ConvertAllFeaturesToTasksView, UpdateGDDWithTaskStatusView, task_status_update_callback)
from .gdd_upload_view import GDDUploadView
from .gdd_structured_views import GDDStructuredCreateView, GDDStructuredEditView, GDDSectionFeatureView, UpdateFeatureOrderView, GDDSimpleCreateView
from .debug_views import debug_tasks_view
from .game_status_view import GameStatusUpdateView
from .education_task_views import EducationTaskDashboardView, EducationTaskBatchUpdateView
from .game_task_create_view import GameDevelopmentTaskCreateView

app_name = 'games'

urlpatterns = [
    # Game Project URLs
    path('', game_views.GameDashboardView.as_view(), name='dashboard'),
    path('list/', game_views.GameProjectListView.as_view(), name='game_list'),
    path('<int:pk>/', game_views.GameProjectDetailView.as_view(), name='game_detail'),
    path('create/', game_views.GameProjectCreateView.as_view(), name='game_create'),
    path('<int:pk>/update/', game_views.GameProjectUpdateView.as_view(), name='game_update'),
    path('<int:pk>/update-status/', GameStatusUpdateView.as_view(), name='game_update_status'),
    
    # Game Design Document URLs
    path('<int:pk>/gdd/', game_views.GameDesignDocumentView.as_view(), name='gdd_detail'),
    # GDD Create URL - redirects to structured create
    path('<int:game_id>/gdd/create/', game_views.GameDesignDocumentCreateView.as_view(), name='gdd_create'),
    path('<int:game_id>/gdd/delete/', GameDesignDocumentDeleteView.as_view(), name='gdd_delete'),
    path('gdd/<int:pk>/edit/', GameDesignDocumentEditView.as_view(), name='gdd_edit'),
    path('tasks/<int:task_id>/link-gdd-section/', TaskGDDSectionLinkView.as_view(), name='task_link_gdd_section'),
    path('<int:pk>/gdd/upload/', GDDUploadView.as_view(), name='gdd_upload'),
    
    # GDD Structured Create URL (User-friendly interface)
    path('<int:game_id>/gdd/structured/create/', GDDSimpleCreateView.as_view(), name='gdd_structured_create'),
    path('<int:game_id>/gdd/simple/create/', GDDSimpleCreateView.as_view(), name='gdd_simple_create'),
    path('gdd/<int:pk>/structured/edit/', GDDStructuredEditView.as_view(), name='gdd_structured_edit'),
    path('<int:game_id>/gdd/section/<str:section_id>/features/', GDDSectionFeatureView.as_view(), name='gdd_section_features'),
    path('<int:game_id>/gdd/section/<int:section_id>/update-order/', UpdateFeatureOrderView.as_view(), name='update_feature_order'),
    
    # GDD Feature Management URLs
    path('gdd/<int:pk>/extract-features/', ExtractFeaturesView.as_view(), name='extract_features'),
    path('gdd/<int:pk>/features/', GDDFeaturesListView.as_view(), name='gdd_features'),
    path('gdd/feature/<int:pk>/convert/', ConvertFeatureToTaskView.as_view(), name='convert_feature'),
    path('gdd/<int:pk>/convert-all-features/', ConvertAllFeaturesToTasksView.as_view(), name='convert_all_features'),
    path('gdd/<int:pk>/update-with-task-status/', UpdateGDDWithTaskStatusView.as_view(), name='update_gdd_with_task_status'),
    path('tasks/<int:task_id>/status-update-callback/', task_status_update_callback, name='task_status_update_callback'),
    
    # GDD Task Management URLs
    path('tasks/<int:pk>/gdd-status-update/', GDDTaskStatusUpdateView.as_view(), name='gdd_task_status_update'),
    path('tasks/batch-update/', BatchTaskUpdateView.as_view(), name='batch_task_update'),
    
    # Game Task Dashboard
    path('tasks/', GameTaskDashboardView.as_view(), name='task_dashboard'),
    path('tasks/game/<int:game_id>/', GameTaskDashboardView.as_view(), name='game_task_dashboard'),
    path('tasks/newtask/', GameDevelopmentTaskCreateView.as_view(), name='task_create'),
    path('tasks/batch-update/', GameTaskBatchUpdateView.as_view(), name='game_task_batch_update'),
    path('tasks/<int:pk>/update_status/', GameTaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/update_hours/', GameTaskHoursUpdateView.as_view(), name='task_hours_update'),
    
    # Game Asset URLs
    path('<int:game_id>/assets/', game_views.GameAssetListView.as_view(), name='asset_list'),
    path('<int:game_id>/assets/create/', game_views.GameAssetCreateView.as_view(), name='asset_create'),
    path('<int:game_id>/assets/<int:asset_id>/', game_views.GameAssetDetailView.as_view(), name='asset_detail'),
    path('<int:game_id>/assets/<int:asset_id>/update/', game_views.GameAssetUpdateView.as_view(), name='asset_update'),
    
    # Game Task URLs
    # Redirect to the game task dashboard with the game_id parameter
    path('<int:game_id>/tasks/', lambda request, game_id: redirect(f'games:game_task_dashboard', game_id=game_id), name='task_list'),
    path('<int:game_id>/tasks/create/', game_views.GameTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', game_views.GameTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', game_views.GameTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', game_views.GameTaskDeleteView.as_view(), name='task_delete'),

    path('<int:game_id>/tasks/kanban/', game_views.GameTaskKanbanView.as_view(), name='task_kanban'),
    
    # Object-oriented task views are now used instead of hybrid views
    
    # Education Task Dashboard is now handled in projects/urls.py
    # path('education/tasks/', EducationTaskDashboardView.as_view(), name='education_task_dashboard'),
    path('education/tasks/batch-update/', EducationTaskBatchUpdateView.as_view(), name='education_batch_task_update'),
    path('debug/tasks/', debug_tasks_view, name='debug_tasks'),
]
