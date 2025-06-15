from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q

# Import game models for dashboard stats
try:
    from projects.game_models import GameProject, GameTask
    GAME_MODELS_AVAILABLE = True
except ImportError:
    GAME_MODELS_AVAILABLE = False


class TestView(View):
    """Simple test view to verify server functionality"""
    def get(self, request):
        return HttpResponse('<h1>Django Server is Working!</h1><p>The R1D3 Game Development System is running.</p>')


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'core/home.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view"""
    template_name = 'core/dashboard.html'
    login_url = '/'  # Temporarily changed from '/accounts/login/' while allauth is disabled
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add game development stats if models are available
        if GAME_MODELS_AVAILABLE:
            # Count active game projects
            context['game_count'] = GameProject.objects.filter(
                status__in=['pre_production', 'production', 'alpha', 'beta']
            ).count()
            
            # Count open tasks
            context['task_count'] = GameTask.objects.filter(
                status__in=['to_do', 'in_progress', 'blocked']
            ).count()
            
            # Get tasks assigned to current user
            context['user_tasks'] = GameTask.objects.filter(
                assigned_to=self.request.user,
                status__in=['to_do', 'in_progress']
            ).order_by('-priority', 'due_date')[:5]
        
        return context
