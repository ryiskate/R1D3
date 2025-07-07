from django.urls import path
from . import views
from .quick_link_views import (
    QuickLinkListView, QuickLinkCreateView, 
    QuickLinkUpdateView, QuickLinkDeleteView, reorder_quick_links
)
from .debug_views import debug_milestones
from .views_milestone import get_milestone_display, test_milestone_update

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # R1D3 Tasks URLs
    path('R1D3-tasks/', views.GlobalTaskDashboardView.as_view(), name='global_task_dashboard'),
    path('R1D3-tasks/newtask/', views.R1D3TaskCreateView.as_view(), name='r1d3_task_create'),
    # Updated URLs with task_type parameter
    path('R1D3-tasks/<str:task_type>/<int:pk>/', views.R1D3TaskDetailView.as_view(), name='r1d3_task_detail'),
    path('R1D3-tasks/<str:task_type>/<int:pk>/update/', views.R1D3TaskUpdateView.as_view(), name='r1d3_task_update'),
    path('R1D3-tasks/<str:task_type>/<int:pk>/delete/', views.R1D3TaskDeleteView.as_view(), name='r1d3_task_delete'),
    # Legacy URLs for backward compatibility
    path('R1D3-tasks/<int:pk>/', views.R1D3TaskDetailLegacyView.as_view(), name='r1d3_task_detail_legacy'),
    path('R1D3-tasks/<int:pk>/update/', views.R1D3TaskUpdateLegacyView.as_view(), name='r1d3_task_update_legacy'),
    path('R1D3-tasks/<int:pk>/delete/', views.R1D3TaskDeleteLegacyView.as_view(), name='r1d3_task_delete_legacy'),
    path('test/', views.TestView.as_view(), name='test'),
    
    # Quick Links URLs
    path('quick-links/', QuickLinkListView.as_view(), name='quick_links'),
    path('quick-links/create/', QuickLinkCreateView.as_view(), name='quick_link_create'),
    path('quick-links/<int:pk>/update/', QuickLinkUpdateView.as_view(), name='quick_link_update'),
    path('quick-links/<int:pk>/delete/', QuickLinkDeleteView.as_view(), name='quick_link_delete'),
    
    # AJAX Task Status Update
    path('R1D3-tasks/update-status/', views.update_task_status, name='update_task_status'),
    path('quick-links/reorder/', reorder_quick_links, name='quick_link_reorder'),
    
    # Milestone display endpoints
    path('milestone-display/', get_milestone_display, name='milestone_display'),
    path('test-milestone-update/', test_milestone_update, name='test_milestone_update'),
    
    # Debug endpoints (only accessible to staff)
    path('api/debug/milestones/', debug_milestones, name='debug_milestones'),
]
