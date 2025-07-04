from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime
import json
from django.template.loader import render_to_string
from django.core.cache import cache

# Import legacy views for backward compatibility
from .legacy_views import R1D3TaskDetailLegacyView, R1D3TaskUpdateLegacyView, R1D3TaskDeleteLegacyView

# Import context processor for milestone data
from .context_processors import breadcrumbs_processor

# Import model utilities
from .model_utils import get_task_model_map, get_task_type_for_model

# Import task models for dashboard stats
TASK_MODELS_AVAILABLE = False
INDIE_NEWS_AVAILABLE = False
try:
    from projects.task_models import (
        R1D3Task, GameDevelopmentTask, EducationTask,
        SocialMediaTask, ArcadeTask, ThemeParkTask
    )
    from projects.game_models import GameTask
    TASK_MODELS_AVAILABLE = True
except ImportError:
    # Models not available, will be imported dynamically when needed
    pass

try:
    from indie_news.models import IndieNewsTask
    INDIE_NEWS_AVAILABLE = True
except ImportError:
    # Indie news models not available
    pass
GAME_MODELS_AVAILABLE = False
IMPORT_ERROR_MESSAGE = ""

try:
    from projects.game_models import GameTask, GameProject
    GAME_MODELS_AVAILABLE = True
except ImportError as e:
    IMPORT_ERROR_MESSAGE += f"Game models import error: {str(e)}\n"

try:
    from projects.task_models import R1D3Task
    TASK_MODELS_AVAILABLE = True
except ImportError as e:
    IMPORT_ERROR_MESSAGE += f"R1D3Task import error: {str(e)}\n"

# Import game project models for dashboard stats
try:
    from projects.game_models import GameProject
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
        user = self.request.user
        
        # Add debugging information
        context['debug_info'] = {
            'username': user.username,
            'user_id': user.id,
            'is_authenticated': user.is_authenticated,
            'task_models_available': TASK_MODELS_AVAILABLE,
            'game_models_available': GAME_MODELS_AVAILABLE
        }
        
        # Add task models availability to context (for internal use only)
        context['task_models_available'] = TASK_MODELS_AVAILABLE
        context['game_models_available'] = GAME_MODELS_AVAILABLE
        
        # Initialize empty lists for tasks
        game_tasks = []
        r1d3_tasks = []
        education_tasks = []
        social_media_tasks = []
        arcade_tasks = []
        theme_park_tasks = []
        indie_news_tasks = []
        
        # Get GameTask objects if game models are available
        if GAME_MODELS_AVAILABLE:
            # Count open game tasks
            context['game_task_count'] = GameTask.objects.filter(
                status__in=['to_do', 'in_progress', 'blocked']
            ).count()
            
            # Get GameTask objects assigned to the current user
            game_tasks = list(GameTask.objects.filter(
                assigned_to=user
            ).order_by('-priority', 'due_date'))
            
            # Add task type information to each game task
            for task in game_tasks:
                task.task_type = 'game'
                
            # Get GameDevelopmentTask objects assigned to the current user
            try:
                game_dev_tasks = list(GameDevelopmentTask.objects.filter(
                    assigned_to=user
                ).order_by('-priority', 'due_date'))
                
                # Add task type information to each Game Development task
                for task in game_dev_tasks:
                    task.task_type = 'game_development'
                    
                # Add game development tasks to the list
                game_tasks.extend(game_dev_tasks)
            except Exception as e:
                print(f"Error loading game development tasks: {e}")
                game_dev_tasks = []
        
        # Get R1D3Task objects assigned to the current user if task models are available
        if TASK_MODELS_AVAILABLE:
            # Count open R1D3 tasks
            context['r1d3_task_count'] = R1D3Task.objects.filter(
                status__in=['to_do', 'in_progress', 'blocked']
            ).count()
            
            # Get R1D3Task objects assigned to the current user
            r1d3_tasks = list(R1D3Task.objects.filter(
                assigned_to=user
            ).order_by('-priority', 'due_date'))
            
            # Print debug info for R1D3 tasks
            print(f"R1D3 tasks for user {user.username}: {len(r1d3_tasks)}")
            for task in r1d3_tasks:
                print(f"  - {task.title} (ID: {task.id})")
            
            # Add task type information to each R1D3 task
            for task in r1d3_tasks:
                task.task_type = 'r1d3'
                
            # Get EducationTask objects assigned to the current user
            try:
                from projects.task_models import EducationTask
                education_tasks = list(EducationTask.objects.filter(
                    assigned_to=user
                ).order_by('-priority', 'due_date'))
                
                # Add task type information to each Education task
                for task in education_tasks:
                    task.task_type = 'education'
            except (ImportError, AttributeError):
                education_tasks = []
                
            # Get SocialMediaTask objects assigned to the current user
            try:
                from projects.task_models import SocialMediaTask
                social_media_tasks = list(SocialMediaTask.objects.filter(
                    assigned_to=user
                ).order_by('-priority', 'due_date'))
                
                # Add task type information to each Social Media task
                for task in social_media_tasks:
                    task.task_type = 'social_media'
            except (ImportError, AttributeError):
                social_media_tasks = []
                
            # Get ArcadeTask objects assigned to the current user
            try:
                from projects.task_models import ArcadeTask
                arcade_tasks = list(ArcadeTask.objects.filter(
                    assigned_to=user
                ).order_by('-priority', 'due_date'))
                
                # Add task type information to each Arcade task
                for task in arcade_tasks:
                    task.task_type = 'arcade'
            except (ImportError, AttributeError):
                arcade_tasks = []
                
            # Get ThemeParkTask objects assigned to the current user
            try:
                from projects.task_models import ThemeParkTask
                theme_park_tasks = list(ThemeParkTask.objects.filter(
                    assigned_to=user
                ).order_by('-priority', 'due_date'))
                
                # Add task type information to each Theme Park task
                for task in theme_park_tasks:
                    task.task_type = 'theme_park'
            except (ImportError, AttributeError):
                theme_park_tasks = []
                
        # Get IndieNewsTask objects assigned to the current user if available
        if INDIE_NEWS_AVAILABLE:
            try:
                indie_news_tasks = list(IndieNewsTask.objects.filter(
                    assigned_to=user
                ).order_by('-priority', 'due_date'))
                
                # Print debug info for indie news tasks
                print(f"Indie News tasks for user {user.username}: {len(indie_news_tasks)}")
                for task in indie_news_tasks:
                    print(f"  - {task.title} (ID: {task.id})")
                
                # Add task type information to each Indie News task
                for task in indie_news_tasks:
                    task.task_type = 'indie_news'
            except Exception as e:
                print(f"Error loading indie news tasks: {e}")
                indie_news_tasks = []
        
        # Combine all tasks
        all_tasks = game_tasks + r1d3_tasks + education_tasks + social_media_tasks + arcade_tasks + theme_park_tasks + indie_news_tasks
        
        # Sort tasks by priority (high to low) and due date (soonest first)
        # Handle tasks with None due_date by using a far future date for sorting
        from datetime import datetime, date
        future_date = date(9999, 12, 31)  # Far future date for sorting
        all_tasks.sort(key=lambda x: (-self.get_priority_value(x.priority), x.due_date or future_date))
        
        # Count tasks by type
        context['game_tasks_count'] = len(game_tasks)
        context['r1d3_tasks_count'] = len(r1d3_tasks)
        context['all_tasks_count'] = len(all_tasks)
        
        # Assign all tasks to context
        context['user_tasks'] = all_tasks
        
        # Add section stats to context
        if GAME_MODELS_AVAILABLE:
            context['game_section_stats'] = {
                'tasks': len(game_tasks),
                'projects': GameProject.objects.filter(status__in=['pre_production', 'production', 'alpha', 'beta']).count()
            }
        
        context['r1d3_section_stats'] = {
            'tasks': len(r1d3_tasks),
        }
        
        # Add quick links to context
        context['quick_links'] = user.quick_links.all()
        
        return context
        
    @staticmethod
    def get_priority_value(priority):
        """Helper function to convert priority string to numeric value for sorting"""
        priority_map = {
            'high': 3,
            'medium': 2,
            'low': 1,
            'none': 0
        }
        return priority_map.get(priority, 0)
        
    @staticmethod
    def get_task_type_from_section(company_section):
        """Helper function to determine task type for URL generation based on company section"""
        section_to_type = {
            'game_development': 'game',
            'education': 'education',
            'arcade': 'arcade',
            'marketing': 'social_media',  # Using social_media for marketing tasks
            'finance': 'finance',
            'hr': 'hr',
            'it': 'it',
            'research': 'research',
            'other': 'r1d3'  # Default to r1d3 for other sections
        }
        return section_to_type.get(company_section, 'r1d3')
        
    @staticmethod
    def get_task_type(task):
        """Legacy helper function for backward compatibility"""
        class_name = task.__class__.__name__
        if class_name == 'GameTask':
            return 'game'
        elif class_name == 'R1D3Task':
            return 'r1d3'
        elif class_name == 'EducationTask' or class_name == 'GameDevelopmentTask' and getattr(task, 'company_section', '') == 'education':
            return 'education'
        elif class_name == 'SocialMediaTask' or class_name == 'GameDevelopmentTask' and getattr(task, 'company_section', '') == 'social_media':
            return 'social_media'
        elif class_name == 'ArcadeTask' or class_name == 'GameDevelopmentTask' and getattr(task, 'company_section', '') == 'arcade':
            return 'arcade'
        elif class_name == 'ThemeParkTask' or class_name == 'GameDevelopmentTask' and getattr(task, 'company_section', '') == 'theme_park':
            return 'theme_park'
        return 'unknown'


class GlobalTaskDashboardView(LoginRequiredMixin, View):
    """Global task dashboard view showing tasks from all company sections"""
    template_name = 'core/global_task_dashboard.html'
    login_url = '/'  # Temporarily changed from '/accounts/login/' while allauth is disabled
    
    def get_template_names(self):
        return [self.template_name]
    
    def get(self, request):
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        assigned_filter = request.GET.get('assigned_to', '')
        company_section_filter = request.GET.get('company_section', '')
        due_date_filter = request.GET.get('due_date', '')
        search_query = request.GET.get('search', '')
        
        # Get all tasks from all available task models
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        # Import indie news tasks
        indie_news_tasks = []
        try:
            from indie_news.models import IndieNewsTask
            indie_news_tasks = list(IndieNewsTask.objects.all())
            print(f"Loaded {len(indie_news_tasks)} indie news tasks")
            # Debug info for indie news tasks
            for task in indie_news_tasks:
                print(f"  - Indie News Task: {task.title} (ID: {task.id})")
        except ImportError as e:
            print(f"IndieNewsTask model not available: {e}")
            pass
        
        # Get tasks from each model
        r1d3_tasks = list(R1D3Task.objects.all())
        game_dev_tasks = list(GameDevelopmentTask.objects.all())
        education_tasks = list(EducationTask.objects.all())
        social_media_tasks = list(SocialMediaTask.objects.all())
        arcade_tasks = list(ArcadeTask.objects.all())
        theme_park_tasks = list(ThemeParkTask.objects.all())
        
        # For backward compatibility, also get tasks from the legacy GameTask model
        game_tasks = list(GameTask.objects.all())
        
        # Add task_type information to each task
        for task in r1d3_tasks:
            task.task_type = 'r1d3'
        
        for task in game_dev_tasks:
            task.task_type = 'game_development'
            
        for task in education_tasks:
            task.task_type = 'education'
            
        for task in social_media_tasks:
            task.task_type = 'social_media'
            
        for task in arcade_tasks:
            task.task_type = 'arcade'
            
        for task in theme_park_tasks:
            task.task_type = 'theme_park'
            
        for task in game_tasks:
            task.task_type = 'game'
            
        # Add task_type information to indie news tasks
        for task in indie_news_tasks:
            task.task_type = 'indie_news'
            
        # Combine all tasks into a single list
        all_tasks = r1d3_tasks + game_dev_tasks + education_tasks + social_media_tasks + arcade_tasks + theme_park_tasks + game_tasks + indie_news_tasks
        
        # Sort tasks by created_at (newest first)
        tasks = sorted(all_tasks, key=lambda x: x.created_at, reverse=True)
        
        # Apply filters - since we're working with a Python list, we need to filter manually
        filtered_tasks = tasks
        
        # Filter by status
        if status_filter and status_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if task.status == status_filter]
        else:
            # By default, exclude tasks with 'done' status unless explicitly requested
            filtered_tasks = [task for task in filtered_tasks if task.status != 'done']
        
        # Filter by priority
        if priority_filter and priority_filter != 'all':
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority_filter]
        
        # Filter by assigned_to
        if assigned_filter == 'me':
            filtered_tasks = [task for task in filtered_tasks if task.assigned_to == request.user]
            print(f"Tasks after assigned_to filter 'me': {len(filtered_tasks)}")
        elif assigned_filter == 'unassigned':
            filtered_tasks = [task for task in filtered_tasks if task.assigned_to is None]
            print(f"Tasks after assigned_to filter 'unassigned': {len(filtered_tasks)}")
        
        # For company section, we need to check the task_type attribute
        if company_section_filter:
            # Use the task_type attribute we added to each task
            filtered_tasks = [task for task in filtered_tasks if task.task_type == company_section_filter]
        
        today = date.today()
        if due_date_filter == 'overdue':
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date < today and task.status in ['to_do', 'in_progress', 'blocked']]
        elif due_date_filter == 'today':
            filtered_tasks = [task for task in filtered_tasks if task.due_date and task.due_date == today]
        elif due_date_filter == 'this_week':
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            filtered_tasks = [task for task in filtered_tasks if task.due_date and today <= task.due_date <= end_of_week]
        
        if search_query:
            filtered_tasks = [task for task in filtered_tasks if 
                             search_query.lower() in task.title.lower() or 
                             (task.description and search_query.lower() in task.description.lower())]
            
        # Update tasks with filtered results
        tasks = filtered_tasks
        
        # Calculate task statistics from the combined task list
        today = date.today()
        task_stats = {
            'total': len(all_tasks),
            'to_do': len([t for t in all_tasks if t.status == 'to_do']),
            'in_progress': len([t for t in all_tasks if t.status == 'in_progress']),
            'in_review': len([t for t in all_tasks if t.status == 'in_review']),
            'done': len([t for t in all_tasks if t.status == 'done']),
            'backlog': len([t for t in all_tasks if t.status == 'backlog']),
            'blocked': len([t for t in all_tasks if t.status == 'blocked']),
            'overdue': len([t for t in all_tasks if t.due_date and t.due_date < today and t.status in ['to_do', 'in_progress', 'blocked']]),
        }
        
        # Calculate section statistics using the new task models
        # Count tasks by type using the specialized task models
        section_stats = [
            {'section_name': 'r1d3', 'count': len(r1d3_tasks)},
            {'section_name': 'game_development', 'count': len(game_dev_tasks) + len([t for t in game_tasks if getattr(t, 'company_section', '') == 'game_development' or not getattr(t, 'company_section', '')])},
            {'section_name': 'education', 'count': len(education_tasks) + len([t for t in game_tasks if getattr(t, 'company_section', '') == 'education'])},
            {'section_name': 'social_media', 'count': len(social_media_tasks) + len([t for t in game_tasks if getattr(t, 'company_section', '') == 'social_media'])},
            {'section_name': 'arcade', 'count': len(arcade_tasks) + len([t for t in game_tasks if getattr(t, 'company_section', '') == 'arcade'])},
            {'section_name': 'theme_park', 'count': len(theme_park_tasks) + len([t for t in game_tasks if getattr(t, 'company_section', '') == 'theme_park'])},
            {'section_name': 'indie_news', 'count': len(indie_news_tasks)},
        ]
        
        # Get recent and upcoming tasks
        recent_tasks = sorted([t for t in all_tasks if t.status == 'done'], key=lambda x: x.updated_at, reverse=True)[:5]
        upcoming_tasks = sorted([t for t in all_tasks if t.due_date and t.due_date >= today and t.status in ['to_do', 'in_progress']], key=lambda x: x.due_date)[:5]
        
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


class R1D3TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new R1D3 task from the global task dashboard.
    This view uses the R1D3Task model and form from the projects app.
    """
    template_name = 'projects/r1d3_task_form.html'
    login_url = '/'  # Redirect to home if not logged in
    
    def get_form_class(self):
        # Import here to avoid circular imports
        from projects.task_forms import R1D3TaskForm
        return R1D3TaskForm
    
    def get_model(self):
        # Import here to avoid circular imports
        from projects.task_models import R1D3Task
        return R1D3Task
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        messages.success(self.request, f"R1D3 Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect back to the global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = "R1D3 Task"
        context['is_create'] = True
        return context


@login_required
@require_POST
def update_task_status(request):
    """AJAX view to update task status directly from the task table."""
    
    # Import the task models if they're not already available
    global R1D3Task, GameDevelopmentTask, EducationTask, SocialMediaTask, ArcadeTask, ThemeParkTask, GameTask
    
    # If the models weren't imported successfully at the module level, try importing them now
    if not TASK_MODELS_AVAILABLE:
        try:
            from projects.task_models import (
                R1D3Task, GameDevelopmentTask, EducationTask,
                SocialMediaTask, ArcadeTask, ThemeParkTask
            )
            from projects.game_models import GameTask
        except ImportError as e:
            return JsonResponse({'error': f'Task models not available: {str(e)}'}, status=500)
    
    # Handle both JSON and form data
    print(f"DEBUG: Content-Type: {request.content_type}")
    print(f"DEBUG: Request method: {request.method}")
    
    # IMPORTANT: We can only read the request body ONCE
    # So we need to be careful not to access both request.POST and request.body
    
    # Check if it's JSON content
    if request.content_type and 'application/json' in request.content_type:
        try:
            # For JSON requests, read the body directly
            data = json.loads(request.body)
            print(f"DEBUG: Parsed JSON data: {data}")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
    else:
        # For form data, use request.POST but don't access request.body
        data = request.POST
        print(f"[DEBUG] Form data: {dict(data)}")
    
    # Log the data we received
    print(f"[DEBUG] Received data: {data}")
    
    
    task_id = data.get('task_id')
    task_type = data.get('task_type')
    status = data.get('status')
    
    print(f"[DEBUG] Task ID: {task_id}, Task Type: {task_type}, Status: {status}")
    
    # Validate required fields
    if not all([task_id, task_type, status]):
        missing = []
        if not task_id: missing.append('task_id')
        if not task_type: missing.append('task_type')
        if not status: missing.append('status')
        print(f"[DEBUG] Missing fields: {missing}")
        return JsonResponse({'error': f'Missing required fields: {missing}'}, status=400)
    
    # Normalize task_type to lowercase for case-insensitive matching
    task_type_lower = task_type.lower()
    
    # Comprehensive model mapping with both snake_case and CamelCase keys
    model_map = {
        # Snake case keys (normalized from frontend)
        'r1d3': R1D3Task,
        'game_development': GameDevelopmentTask,
        'education': EducationTask,
        'social_media': SocialMediaTask,
        'arcade': ArcadeTask,
        'theme_park': ThemeParkTask,
        'game': GameTask,
        # Class name keys (from template filter)
        'r1d3task': R1D3Task,
        'gamedevelopmenttask': GameDevelopmentTask,
        'educationtask': EducationTask,
        'socialmediatask': SocialMediaTask,
        'arcadetask': ArcadeTask,
        'themeparktask': ThemeParkTask,
        'gametask': GameTask,
    }
    
    # Try to get model using case-insensitive matching
    model = None
    for key, value in model_map.items():
        if key.lower() == task_type_lower:
            model = value
            break
    
    if not model:
        print(f"[DEBUG] Invalid task type: {task_type}")
        return JsonResponse({'error': f'Invalid task type: {task_type}'}, status=400)
    
    print(f"[DEBUG] Using model: {model.__name__}")
    
    try:
        task = model.objects.get(pk=task_id)
        print(f"[DEBUG] Found task: {task}")
    except model.DoesNotExist:
        print(f"[DEBUG] Task not found: {task_id}")
        return JsonResponse({'error': f'Task not found: {task_id}'}, status=404)
    except ValueError as e:
        print(f"[DEBUG] Invalid task ID: {task_id}, Error: {e}")
        return JsonResponse({'error': f'Invalid task ID: {task_id}'}, status=400)
    
    valid_statuses = ['to_do', 'in_progress', 'in_review', 'done', 'backlog', 'blocked']
    if status not in valid_statuses:
        print(f"[DEBUG] Invalid status: {status}")
        return JsonResponse({'error': f'Invalid status: {status}'}, status=400)

    old_status = task.status
    print(f"[DEBUG] Updating status from {old_status} to {status}")
    task.status = status
    task.save(update_fields=['status'])
    print(f"[DEBUG] Task status updated successfully - ID: {task_id}, Old: {old_status}, New: {status}")

    # Return success response
    return JsonResponse({
        'success': True,
        'task_id': task_id,
        'status': status,
        'status_display': task.get_status_display() if hasattr(task, 'get_status_display') else status.replace('_', ' ').title()
    })


class R1D3TaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    Can redirect to section-specific URLs for specialized task types.
    """
    template_name = 'projects/r1d3_task_form.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get(self, request, *args, **kwargs):
        """Override get method to redirect to section-specific URLs when appropriate"""
        from django.shortcuts import redirect
        
        task_type = self.kwargs.get('task_type')
        task_id = self.kwargs.get('pk')
        
        # Map of task types to their section-specific URL names
        section_url_map = {
            'theme_park': 'theme_park:task_update',
            'arcade': 'arcade:task_update',
            'social_media': 'social_media:task_update',
            'education': 'education:task_update',
            'game_development': 'games:task_update',
            # Add other sections as needed
        }
        
        # If this task type should be redirected to a section-specific URL
        if task_type in section_url_map:
            return redirect(section_url_map[task_type], pk=task_id)
        
        # Default behavior for R1D3 tasks or if redirection fails
        return super().get(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        # Import task models here to avoid circular imports
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Map task_type to model
        model_map = {
            'r1d3': R1D3Task,
            'game_development': GameDevelopmentTask,
            'education': EducationTask,
            'social_media': SocialMediaTask,
            'arcade': ArcadeTask,
            'theme_park': ThemeParkTask,
        }
        
        # Get the appropriate model based on task_type
        model = model_map.get(task_type)
        if not model:
            raise Http404(f"Invalid task type: {task_type}")
        
        try:
            task = model.objects.get(pk=task_id)
            # Set the appropriate form class and template based on task type
            self._set_task_specifics(model.__name__)
            return task
        except model.DoesNotExist:
            raise Http404(f"No {task_type} task found with ID {task_id}")
    
    def _set_task_specifics(self, model_name):
        # Set form class and template based on task type
        if model_name == 'GameDevelopmentTask':
            from projects.task_forms import GameDevelopmentTaskForm
            self.form_class = GameDevelopmentTaskForm
            self.template_name = 'projects/game_task_form.html'
            self.section_name = 'Game Development Task'
        elif model_name == 'EducationTask':
            from projects.task_forms import EducationTaskForm
            self.form_class = EducationTaskForm
            self.template_name = 'projects/education_task_form.html'
            self.section_name = 'Education Task'
        elif model_name == 'SocialMediaTask':
            from projects.task_forms import SocialMediaTaskForm
            self.form_class = SocialMediaTaskForm
            self.template_name = 'projects/social_media_task_form.html'
            self.section_name = 'Social Media Task'
        elif model_name == 'ArcadeTask':
            from projects.task_forms import ArcadeTaskForm
            self.form_class = ArcadeTaskForm
            self.template_name = 'projects/arcade_task_form.html'
            self.section_name = 'Arcade Task'
        elif model_name == 'ThemeParkTask':
            from projects.task_forms import ThemeParkTaskForm
            self.form_class = ThemeParkTaskForm
            self.template_name = 'projects/theme_park_task_form.html'
            self.section_name = 'Theme Park Task'
        else:  # Default to R1D3Task
            from projects.task_forms import R1D3TaskForm
            self.form_class = R1D3TaskForm
            self.template_name = 'projects/r1d3_task_form.html'
            self.section_name = 'R1D3 Task'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Import and use the subtask handler
        from core.subtask_handler import handle_subtasks
        handle_subtasks(self.request, form.instance)
        
        messages.success(self.request, f"Task '{form.instance.title}' updated successfully!")
        return response
    
    def get_success_url(self):
        # Redirect back to the global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
        context['is_update'] = True
        
        # Get existing subtasks for this task if it exists
        if self.object and self.object.pk:
            from core.task_utils import get_task_subtasks
            context['subtasks'] = get_task_subtasks(self.object)
        
        return context


class R1D3TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    """
    template_name = 'projects/task_confirm_delete.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get_object(self, queryset=None):
        # Import task models here to avoid circular imports
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Map task_type to model
        model_map = {
            'r1d3': R1D3Task,
            'game_development': GameDevelopmentTask,
            'education': EducationTask,
            'social_media': SocialMediaTask,
            'arcade': ArcadeTask,
            'theme_park': ThemeParkTask,
        }
        
        # Get the appropriate model based on task_type
        model = model_map.get(task_type)
        if not model:
            raise Http404(f"Invalid task type: {task_type}")
        
        try:
            task = model.objects.get(pk=task_id)
            # Set the appropriate template and section name based on task type
            self._set_task_specifics(model.__name__)
            return task
        except model.DoesNotExist:
            raise Http404(f"No {task_type} task found with ID {task_id}")
    
    def _set_task_specifics(self, model_name):
        # Set template and section name based on task type
        if model_name == 'GameDevelopmentTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Game Development Task'
            self.active_department = 'game_dev'
        elif model_name == 'EducationTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Education Task'
            self.active_department = 'education'
        elif model_name == 'SocialMediaTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Social Media Task'
            self.active_department = 'social_media'
        elif model_name == 'ArcadeTask':
            self.template_name = 'arcade/task_confirm_delete.html'
            self.section_name = 'Arcade Task'
            self.active_department = 'arcade'
        elif model_name == 'ThemeParkTask':
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'Theme Park Task'
            self.active_department = 'theme_park'
        else:  # Default to R1D3Task
            self.template_name = 'projects/task_confirm_delete.html'
            self.section_name = 'R1D3 Task'
            self.active_department = 'r1d3'
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_title = task.title  # Store the title before deletion
        messages.success(request, f"{self.section_name} '{task_title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        # Redirect back to the global task dashboard
        return reverse_lazy('core:global_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
        context['active_department'] = getattr(self, 'active_department', 'r1d3')
        # Get subtasks for this task
        from core.task_utils import get_task_subtasks
        context['subtasks'] = get_task_subtasks(self.object)
        
        return context


class R1D3TaskDetailView(LoginRequiredMixin, DetailView):
    """
    View an existing task from the global task dashboard.
    This view uses the task_type parameter to determine which model to use.
    Can redirect to section-specific URLs for specialized task types.
    """
    template_name = 'projects/r1d3_task_detail.html'
    login_url = '/'  # Redirect to home if not logged in
    context_object_name = 'task'
    
    def get(self, request, *args, **kwargs):
        """Override get method to redirect to section-specific URLs when appropriate"""
        from django.shortcuts import redirect
        from django.http import Http404
        
        task_type = self.kwargs.get('task_type')
        task_id = self.kwargs.get('pk')
        
        # Map of task types to their section-specific URL names
        section_url_map = {
            'theme_park': 'theme_park:task_detail',
            'arcade': 'arcade:task_detail',
            'social_media': 'social_media:task_detail',
            'education': 'education:task_detail',
            'game_development': 'games:task_detail',
            # Add other sections as needed
        }
        
        # If this task type should be redirected to a section-specific URL
        if task_type in section_url_map:
            return redirect(section_url_map[task_type], pk=task_id)
        
        # Default behavior for R1D3 tasks or if redirection fails
        return super().get(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        # Import task models here to avoid circular imports
        from projects.task_models import (
            R1D3Task, GameDevelopmentTask, EducationTask,
            SocialMediaTask, ArcadeTask, ThemeParkTask
        )
        
        task_id = self.kwargs.get('pk')
        task_type = self.kwargs.get('task_type')
        
        # Map task_type to model
        model_map = {
            'r1d3': R1D3Task,
            'game_development': GameDevelopmentTask,
            'education': EducationTask,
            'social_media': SocialMediaTask,
            'arcade': ArcadeTask,
            'theme_park': ThemeParkTask,
        }
        
        # Get the appropriate model based on task_type
        model = model_map.get(task_type)
        if not model:
            raise Http404(f"Invalid task type: {task_type}")
        
        try:
            task = model.objects.get(pk=task_id)
            # Set the appropriate template and section name based on task type
            self._set_task_specifics(model.__name__)
            return task
        except model.DoesNotExist:
            raise Http404(f"No {task_type} task found with ID {task_id}")
    
    def _set_task_specifics(self, model_name):
        # Set template and section name based on task type
        if model_name == 'GameDevelopmentTask':
            self.template_name = 'projects/game_task_detail.html'
            self.section_name = 'Game Development Task'
            self.active_department = 'game_dev'
        elif model_name == 'EducationTask':
            self.template_name = 'projects/education_task_detail.html'
            self.section_name = 'Education Task'
            self.active_department = 'education'
        elif model_name == 'SocialMediaTask':
            self.template_name = 'projects/social_media_task_detail.html'
            self.section_name = 'Social Media Task'
            self.active_department = 'social_media'
        elif model_name == 'ArcadeTask':
            self.template_name = 'arcade/task_detail.html'
            self.section_name = 'Arcade Task'
            self.active_department = 'arcade'
        elif model_name == 'ThemeParkTask':
            self.template_name = 'theme_park/task_detail.html'
            self.section_name = 'Theme Park Task'
            self.active_department = 'theme_park'
        else:  # Default to R1D3Task
            self.template_name = 'projects/r1d3_task_detail.html'
            self.section_name = 'R1D3 Task'
            self.active_department = 'r1d3'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = getattr(self, 'section_name', 'Task')
        context['active_department'] = getattr(self, 'active_department', 'r1d3')
        # Get subtasks for this task
        from core.task_utils import get_task_subtasks
        context['subtasks'] = get_task_subtasks(self.object)
        
        return context
