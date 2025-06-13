from django.urls import path
from . import views

app_name = 'strategy'

urlpatterns = [
    path('', views.StrategyDashboardView.as_view(), name='dashboard'),
    path('visions/', views.VisionListView.as_view(), name='vision_list'),
    path('visions/<int:pk>/', views.VisionDetailView.as_view(), name='vision_detail'),
    path('visions/create/', views.VisionCreateView.as_view(), name='vision_create'),
    path('goals/', views.GoalListView.as_view(), name='goal_list'),
    path('goals/<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('objectives/', views.ObjectiveListView.as_view(), name='objective_list'),
]
