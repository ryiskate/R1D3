from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from datetime import date, timedelta

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


class GlobalTaskDashboardView(LoginRequiredMixin, View):
    """Global task dashboard view showing tasks from all company sections"""
    template_name = 'core/global_task_dashboard.html'
    login_url = '/'  # Temporarily changed from '/accounts/login/' while allauth is disabled
    
    def get(self, request):
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        assigned_filter = request.GET.get('assigned_to', '')
        company_section_filter = request.GET.get('company_section', '')
        due_date_filter = request.GET.get('due_date', '')
        search_query = request.GET.get('search', '')
        
        # Start with all tasks
        tasks = GameTask.objects.all()
        
        # Apply filters
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        if assigned_filter == 'me':
            tasks = tasks.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        
        if company_section_filter:
            tasks = tasks.filter(company_section=company_section_filter)
        
        if due_date_filter == 'overdue':
            tasks = tasks.filter(due_date__lt=date.today(), status__in=['to_do', 'in_progress', 'blocked'])
        elif due_date_filter == 'today':
            tasks = tasks.filter(due_date=date.today())
        elif due_date_filter == 'this_week':
            today = date.today()
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            tasks = tasks.filter(due_date__range=[today, end_of_week])
        
        if search_query:
            tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
        # Get task statistics
        task_stats = {
            'total': GameTask.objects.count(),
            'to_do': GameTask.objects.filter(status='to_do').count(),
            'in_progress': GameTask.objects.filter(status='in_progress').count(),
            'in_review': GameTask.objects.filter(status='in_review').count(),
            'done': GameTask.objects.filter(status='done').count(),
            'backlog': GameTask.objects.filter(status='backlog').count(),
            'blocked': GameTask.objects.filter(status='blocked').count(),
            'overdue': GameTask.objects.filter(due_date__lt=date.today(), status__in=['to_do', 'in_progress', 'blocked']).count(),
        }
        
        # Get tasks by company section
        section_stats = GameTask.objects.values('company_section').annotate(
            count=Count('id'),
            section_name=F('company_section')
        ).order_by('company_section')
        
        # Get recent and upcoming tasks
        recent_tasks = GameTask.objects.filter(status='done').order_by('-updated_at')[:5]
        upcoming_tasks = GameTask.objects.filter(
            due_date__gte=date.today(),
            status__in=['to_do', 'in_progress']
        ).order_by('due_date')[:5]
        
        context = {
            'tasks': tasks,
            'task_stats': task_stats,
            'section_stats': section_stats,
            'recent_tasks': recent_tasks,
            'upcoming_tasks': upcoming_tasks,
            'today': date.today(),
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'assigned_filter': assigned_filter,
            'company_section_filter': company_section_filter,
            'due_date_filter': due_date_filter,
            'search_query': search_query,
        }
        
        return render(request, self.template_name, context)


class SocialMediaTaskDashboardView(LoginRequiredMixin, View):
    """Social Media task dashboard view showing tasks from the social media section"""
    template_name = 'core/social_task_dashboard.html'
    login_url = '/'
    
    def get(self, request):
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        assigned_filter = request.GET.get('assigned_to', '')
        platform_filter = request.GET.get('platform', '')
        due_date_filter = request.GET.get('due_date', '')
        search_query = request.GET.get('search', '')
        
        # Start with all social media tasks
        tasks = GameTask.objects.filter(company_section='social_media')
        
        # Apply filters
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        if assigned_filter == 'me':
            tasks = tasks.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        
        if platform_filter:
            tasks = tasks.filter(platform=platform_filter)
        
        if due_date_filter == 'overdue':
            tasks = tasks.filter(due_date__lt=date.today(), status__in=['to_do', 'in_progress', 'blocked'])
        elif due_date_filter == 'today':
            tasks = tasks.filter(due_date=date.today())
        elif due_date_filter == 'this_week':
            today = date.today()
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            tasks = tasks.filter(due_date__range=[today, end_of_week])
        
        if search_query:
            tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
        # Get task statistics
        task_stats = {
            'total': tasks.count(),
            'to_do': tasks.filter(status='to_do').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'done': tasks.filter(status='done').count(),
            'backlog': tasks.filter(status='backlog').count(),
            'blocked': tasks.filter(status='blocked').count(),
            'overdue': tasks.filter(due_date__lt=date.today(), status__in=['to_do', 'in_progress', 'blocked']).count(),
        }
        
        # Get tasks by social media platform
        platform_stats = {
            'twitter': tasks.filter(platform='twitter').count(),
            'instagram': tasks.filter(platform='instagram').count(),
            'facebook': tasks.filter(platform='facebook').count(),
            'youtube': tasks.filter(platform='youtube').count(),
            'linkedin': tasks.filter(platform='linkedin').count(),
            'tiktok': tasks.filter(platform='tiktok').count(),
        }
        
        # Get recent and upcoming tasks
        recent_tasks = tasks.filter(status='done').order_by('-updated_at')[:5]
        upcoming_tasks = tasks.filter(
            due_date__gte=date.today(),
            status__in=['to_do', 'in_progress']
        ).order_by('due_date')[:5]
        
        context = {
            'tasks': tasks,
            'task_stats': task_stats,
            'platform_stats': platform_stats,
            'recent_tasks': recent_tasks,
            'upcoming_tasks': upcoming_tasks,
            'today': date.today(),
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'assigned_filter': assigned_filter,
            'platform_filter': platform_filter,
            'due_date_filter': due_date_filter,
            'search_query': search_query,
            'current_filters': any([status_filter, priority_filter, assigned_filter, platform_filter, due_date_filter, search_query]),
        }
        
        return render(request, self.template_name, context)
