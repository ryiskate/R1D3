from django.urls import path
from . import views

app_name = 'indie_news'

urlpatterns = [
    # Task URLs
    path('tasks/', views.IndieNewsTaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.IndieNewsTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.IndieNewsTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.IndieNewsTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.IndieNewsTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/batch-update/', views.IndieNewsTaskBatchUpdateView.as_view(), name='task_batch_update'),
    
    # Game URLs
    path('games/', views.IndieGameListView.as_view(), name='game_list'),
    path('games/create/', views.IndieGameCreateView.as_view(), name='game_create'),
    path('games/<int:pk>/', views.IndieGameDetailView.as_view(), name='game_detail'),
    path('games/<int:pk>/update/', views.IndieGameUpdateView.as_view(), name='game_update'),
    path('games/<int:pk>/delete/', views.IndieGameDeleteView.as_view(), name='game_delete'),
    
    # Event URLs
    path('events/', views.IndieEventListView.as_view(), name='event_list'),
    path('events/create/', views.IndieEventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.IndieEventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/update/', views.IndieEventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.IndieEventDeleteView.as_view(), name='event_delete'),
    
    # Tool URLs
    path('tools/', views.IndieToolListView.as_view(), name='tool_list'),
    path('tools/create/', views.IndieToolCreateView.as_view(), name='tool_create'),
    path('tools/<int:pk>/', views.IndieToolDetailView.as_view(), name='tool_detail'),
    path('tools/<int:pk>/update/', views.IndieToolUpdateView.as_view(), name='tool_update'),
    path('tools/<int:pk>/delete/', views.IndieToolDeleteView.as_view(), name='tool_delete'),
    
    # Dashboard URL (main entry point)
    path('', views.IndieNewsDashboardView.as_view(), name='dashboard'),
]
