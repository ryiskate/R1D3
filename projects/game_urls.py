from django.urls import path
from . import game_views
from .task_status_update_view import TaskStatusUpdateView
from .gdd_views import GameDesignDocumentEditView, TaskGDDSectionLinkView
from .gdd_feature_views import ExtractFeaturesView, GDDFeaturesListView, ConvertFeatureToTaskView, ConvertAllFeaturesToTasksView, UpdateGDDWithTaskStatusView, task_status_update_callback
from .gdd_upload_view import GDDUploadView

app_name = 'games'

urlpatterns = [
    # Game Project URLs
    path('', game_views.GameDashboardView.as_view(), name='dashboard'),
    path('list/', game_views.GameProjectListView.as_view(), name='game_list'),
    path('<int:pk>/', game_views.GameProjectDetailView.as_view(), name='game_detail'),
    path('create/', game_views.GameProjectCreateView.as_view(), name='game_create'),
    
    # Game Design Document URLs
    path('<int:pk>/gdd/', game_views.GameDesignDocumentView.as_view(), name='gdd_detail'),
    path('<int:game_id>/gdd/create/', game_views.GameDesignDocumentCreateView.as_view(), name='gdd_create'),
    path('gdd/<int:pk>/edit/', GameDesignDocumentEditView.as_view(), name='gdd_edit'),
    path('tasks/<int:task_id>/link-gdd-section/', TaskGDDSectionLinkView.as_view(), name='task_link_gdd_section'),
    path('<int:pk>/gdd/upload/', GDDUploadView.as_view(), name='gdd_upload'),
    
    # GDD Feature Management URLs
    path('gdd/<int:pk>/extract-features/', ExtractFeaturesView.as_view(), name='extract_features'),
    path('gdd/<int:pk>/features/', GDDFeaturesListView.as_view(), name='gdd_features'),
    path('gdd/feature/<int:pk>/convert/', ConvertFeatureToTaskView.as_view(), name='convert_feature'),
    path('gdd/<int:pk>/convert-all-features/', ConvertAllFeaturesToTasksView.as_view(), name='convert_all_features'),
    path('gdd/<int:pk>/update-with-task-status/', UpdateGDDWithTaskStatusView.as_view(), name='update_gdd_with_task_status'),
    path('tasks/<int:task_id>/status-update-callback/', task_status_update_callback, name='task_status_update_callback'),
    
    # Game Asset URLs
    path('<int:game_id>/assets/', game_views.GameAssetListView.as_view(), name='asset_list'),
    path('<int:game_id>/assets/create/', game_views.GameAssetCreateView.as_view(), name='asset_create'),
    path('<int:game_id>/assets/<int:asset_id>/', game_views.GameAssetDetailView.as_view(), name='asset_detail'),
    path('<int:game_id>/assets/<int:asset_id>/update/', game_views.GameAssetUpdateView.as_view(), name='asset_update'),
    
    # Game Task URLs
    path('<int:game_id>/tasks/', game_views.GameTaskListView.as_view(), name='task_list'),
    path('<int:game_id>/tasks/create/', game_views.GameTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', game_views.GameTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', game_views.GameTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', game_views.GameTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/status-update/', TaskStatusUpdateView.as_view(), name='task_status_update'),
    path('<int:game_id>/tasks/kanban/', game_views.GameTaskKanbanView.as_view(), name='task_kanban'),
]
