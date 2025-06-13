from django.urls import path
from . import game_views

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
    
    # Game Asset URLs
    path('<int:game_id>/assets/', game_views.GameAssetListView.as_view(), name='asset_list'),
    path('<int:game_id>/assets/create/', game_views.GameAssetCreateView.as_view(), name='asset_create'),
    
    # Game Task URLs
    path('<int:game_id>/tasks/', game_views.GameTaskListView.as_view(), name='task_list'),
    path('<int:game_id>/tasks/create/', game_views.GameTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', game_views.GameTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', game_views.GameTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', game_views.GameTaskDeleteView.as_view(), name='task_delete'),
    path('<int:game_id>/tasks/kanban/', game_views.GameTaskKanbanView.as_view(), name='task_kanban'),
]
