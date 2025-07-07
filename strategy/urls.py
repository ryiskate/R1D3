from django.urls import path
from . import views
from . import debug_views

app_name = 'strategy'

urlpatterns = [
    path('', views.StrategyDashboardView.as_view(), name='dashboard'),
    path('visions/', views.VisionListView.as_view(), name='vision_list'),
    path('visions/<int:pk>/', views.VisionDetailView.as_view(), name='vision_detail'),
    path('visions/create/', views.VisionCreateView.as_view(), name='vision_create'),
    path('goals/', views.GoalListView.as_view(), name='goal_list'),
    path('goals/<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('objectives/', views.ObjectiveListView.as_view(), name='objective_list'),
    
    # Debug URLs
    path('debug/milestone/', debug_views.MilestoneDebugView.as_view(), name='debug_milestone'),
    
    # Company Strategy Roadmap URLs
    path('company-strategy/', views.CompanyStrategyView.as_view(), name='company_strategy'),  # Keep for backward compatibility
    path('', views.CompanyStrategyView.as_view(), name='dashboard'),  # Make dashboard show company strategy
    path('company-strategy/phase/<int:pk>/', views.StrategyPhaseDetailView.as_view(), name='phase_detail'),
    path('company-strategy/phase/<int:pk>/edit/', views.PhaseEditRedirectView.as_view(), name='phase_edit_redirect'),
    path('company-strategy/phase/create/', views.PhaseCreateRedirectView.as_view(), name='phase_create_redirect'),
    # Using the View class directly since we don't have a StrategyMilestoneCreateView class
    path('company-strategy/phase/<int:phase_id>/milestone/create/', views.View.as_view(), name='milestone_create'),
    path('company-strategy/phase/<int:phase_id>/milestone/<int:milestone_id>/edit/', views.StrategyMilestoneUpdateView.as_view(), name='milestone_update'),
    path('company-strategy/phase/<int:phase_id>/milestone/<int:milestone_id>/delete/', views.StrategyMilestoneDeleteView.as_view(), name='milestone_delete'),
]
